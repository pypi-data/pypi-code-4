import os
from fabric.api import cd, run, settings

from utils import prepare_folder


possible_version_type = {
    'app' : '--app-version',
    'env' : '--env-version',
    'service' : '--service-version',
    }


def checkout_branch(folder, url, branch):
    """
    Checks out the given branch from the GitHub repo at :attr:`url`.
    Returns the long SHA of the branch's HEAD.
    """
    with settings(warn_only=True):
        if run("test -d %s/.git" % folder).failed:
            run("git clone --depth=100 --quiet %s %s" % (url, folder))

    with cd(folder):
        run("git fetch --quiet origin")
        run("git reset --quiet --hard origin/%s" % branch)
        run("git submodule --quiet init")
        run("git submodule --quiet update")
        return run('git rev-parse HEAD')


def build(path_to_missile,
          output_path,
          version_suffix,
          webcallback_suffix):
    """
    Actually trigger the build via trebuchet.
    """
    command = "trebuchet build %s --arch amd64 --output %s %s %s" \
                    % (path_to_missile,
                       output_path,
                       version_suffix,
                       webcallback_suffix)
    run(command)


def lint(path_to_missile):
    """
    Lint the configuration and output the list of packages that are actually going to be built.
    """
    package_list_leader = 'Packages to be built: '
    output = run("trebuchet lint %s" % path_to_missile)
    for line in output.splitlines():
        if line.startswith(package_list_leader):
            names = line[len(package_list_leader):]
            return [name.strip() for name in names.split(',')]
    raise ValueError("No package list found.")


class WorkingCopy(object):
    """
    Location where the packages will be built upon, handled by Git as a working copy.
    """
    def __init__(self, name, base_folder=None):
        self.name = name
        self.versions = {}

        # Specify the temp folder where the operations will take place (default is /tmp/gachette/working_copy)
        if base_folder is None:
            base_folder = os.path.join('/', 'tmp', 'gachette')
        self.working_copy = os.path.join(base_folder, 'working_copy', name)


    def set_version(self, app=None, env=None, service=None):
        """
        Setup manually the versions if needed.
        """
        if app is not None:
            self.versions['app'] = app
        if env is not None:
            self.versions['env'] = env
        if service is not None:
            self.versions['service'] = service

    def get_version_suffix(self):
        output = ""
        for key in sorted(possible_version_type.iterkeys()):
            if key in self.versions and \
                      (self.versions[key] or self.versions[key] != ""):
                output += " %s %s" % (possible_version_type[key],
                                      self.versions[key])
        return output


    def get_webcallback_suffix(self, webcallback):
        return '--web-callback "%s"' % webcallback if webcallback else ''

    def prepare_environment(self):
        """
        Create or empty working copy folder if exists.
        """
        prepare_folder(self.working_copy, clean=True)

    def checkout_working_copy(self, url, branch):
        """
        Checkout code in the working copy. Returns the long SHA of the
        branch's HEAD
        """
        return checkout_branch(self.working_copy, url, branch)

    def get_missile_path(self):
        return os.path.join(self.working_copy, ".missile.yml")

    def lint(self, path_to_missile=None):
        """
        Lint the package configuration with trebuchet and return the list of
        package names that will be built.
        """
        if not path_to_missile:
            path_to_missile = self.get_missile_path()

        with cd(self.working_copy):
            return lint(path_to_missile)

    def build(self, output_path, path_to_missile=None, webcallback=None):
        """
        Build packages with trebuchet.
        """
        if not path_to_missile:
            path_to_missile = self.get_missile_path()

        with cd(self.working_copy):
            build(path_to_missile,
                    output_path,
                    self.get_version_suffix(),
                    self.get_webcallback_suffix(webcallback))
