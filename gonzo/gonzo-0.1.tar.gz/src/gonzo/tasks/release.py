import os
import gzip

from fabric.api import task, require, env, sudo, put, run
from fabric.contrib.files import exists, append
import git

NEXT, PREVIOUS = 1, -1
DEFAULT_ARCHIVE_DIR = "./release_cache"


def activate_command():
    return ('cd /srv/%s/; source bin/activate; '
            'cd releases/%s/%s'.format(env.project, env.commit))


def history_path(project, project_root='/srv'):
    return os.path.join(project_root, project, 'releases/.history')


def get_releases(project_root, project):
    if not exists(history_path(project)):
        raise Exception("No history!")

    releases = run('cat {}'.format(history_path(project)))
    return [l.strip() for l in releases.splitlines()]


def get_adjacent_release(project_root, project, current_release,
                         direction=NEXT):
    """ Return next or previous release from the history file according to
        direction which is NEXT (1) or PREVIOUS (-1).

        If current_release is None then pick first or last entry if
        PREVIOUS / NEXT
    """
    releases = get_releases(project_root, project)

    new_release = None
    if not current_release:
        try:
            new_release = releases[-1] if direction == NEXT else releases[0]
        except IndexError:
            new_release = None
    else:
        try:
            current_index = releases.index(current_release)
            next_index = current_index + direction
            if next_index < 0:
                new_release = None
            else:
                new_release = releases[next_index]
        except ValueError:
            # raised if the current release is not found
            new_release = None
        except IndexError:
            # reaised if the adjacent index is out of range
            new_release = None

    return new_release


def get_repo():
    """ Return a git.Repo object, caching it if not already in cache. """
    if not getattr(get_repo, "repo", None):
        cwd = os.getcwd()
        get_repo.repo = git.Repo(cwd)

    return get_repo.repo


def get_archive_name(commit_id, project, cache_dir=DEFAULT_ARCHIVE_DIR):
    """ Utility method to return fully qualified path to a cache file """

    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    proj_cache_dir = "%s/%s" % (cache_dir, project)
    cache_dir = os.path.realpath(proj_cache_dir)
    if not os.path.exists(proj_cache_dir):
        os.mkdir(proj_cache_dir)

    if not os.path.isdir(proj_cache_dir):
        raise Exception("Cache dir specified is not a directory!")

    return os.path.join(proj_cache_dir, "%s.tgz" % commit_id)


def create_archive(project, commit_id, cache_dir=DEFAULT_ARCHIVE_DIR):
    """ Create a tgz archive from the specified commit ID in the named project.
        Output file is in cache_dir which defaults to release_cache under the
        current working directory - it is created if it does not exist. File
        name is <commit_id>.tgz

        Returns (tarfile path, False) if the archive already exists;
        (tarfile path, True) if it is created.
    """

    tarfile = get_archive_name(commit_id, project, cache_dir)
    if os.path.isfile(tarfile):
        return (tarfile, False)

    _git = get_repo().git
    try:
        # the prefix used on the remote server for releases to live
        prefix = '/srv/{0}/releases/{1}/{0}/'.format(project, commit_id)
        with gzip.open(tarfile, "wb") as outfile:
            outfile.write(_git.archive(commit_id, format="tar", prefix=prefix))
    except git.exc.GitCommandError:
        os.remove(tarfile)
        raise Exception("Invalid commit ID: %s " % commit_id)

    return (tarfile, True)


def set_history(project, release):
    """ Append the release to the .history file unless it already exists in
        there.
    """
    # this fabric command does what we want here
    append(history_path(project), '{}\n'.format(release), use_sudo=True)


def register_release(project_root, project, release, chown_dirs='www-data'):
    """ Registers a newly pushed release by setting permissions and recording
        the release in the history file. To make active, a rollforward is
        needed subsequently.
    """
    target_release = os.path.join(project_root, project, "releases", release)

    if not os.path.exists(target_release):
        raise Exception("Target release %s not found" % target_release)

    if chown_dirs:
        sudo("chown -R {} {}".format(chown_dirs, target_release))

    set_history(project, release)


def get_active_branch():
    """ Return active branch for the specified repo """
    return get_repo().active_branch.name


def last_commit(branch=None):
    """ Return the last commit ID for the named branch, or the currently active
        branch if not specified
    """

    if not branch:
        branch = get_active_branch()

    return commit_by_name(branch)


def commit_by_name(name):
    """ Will check to see if name is a branch, and if so return the last commit
        ID on that branch, or if a commit ID in which case will return the full
        commit ID. If neither, raises exception.
    """
    repo = get_repo()

    try:
        commit = repo.commit(name)
        return commit.hexsha
    except git.BadObject:
        raise Exception("Invalid name: %s " % name)


def purge(project_root, project, release):
    """ Purge package file for the particular release.

        Removes the cached file in ``project_root/project/packages`` and remove
        the untarred directory and remove history entry only if this is not the
        target of the 'current' pointer
    """
    package_name = os.path.join(
        project_root, project, 'packages', '%s.tgz' % release)
    released_dir = os.path.join(project_root, project, 'releases', release)
    history_file = os.path.join(project_root, project, 'releases', '.history')
    current_pointer = current()

    if exists(package_name):
        sudo('rm {}'.format(package_name))

    if current_pointer == release:
        raise Exception(
            "Cannot remove checked out directory as it is the current release")

    sudo('rm -rf {}'.format(released_dir))

    # remove history entry
    releases = get_releases(project_root, project)
    releases = [v for v in releases if v.strip()]
    sudo('cat << EOF > {}\n{}\nEOF'.format(history_file, '\n'.join(releases)))


def roll_history(project, project_root='/srv', direction=NEXT):
    """ Roll the current release back or forward to the adjacent one in the
        history file. if no current pointer exists, it is assumed that the last
        (most recent) entry in the history file is the one to link if rolling
        forward, and the first (earliest) entry is the one to link if rolling
        backwards.

        Rolling forward is the key step to make a release live after
        registering a release. Restarting any processes running the old code is
        also required.
    """
    FIRST_TIME = True
    current = os.path.join(project_root, project, "releases", "current")

    if exists(current):
        FIRST_TIME = False
        current_release = current()
    else:
        current_release = None

    next_release = get_adjacent_release(
        project_root, project, current_release, direction)

    if not next_release:
        raise Exception("No release to which to roll %s" %
                        {PREVIOUS: "back", NEXT: "forward"}[direction])

    next_release = os.path.join(project_root, project, "releases", next_release)
    if not FIRST_TIME:
        sudo('rm {}'.format(current))
    sudo('ln -s {0} {1}'.format(next_release, current))


@task
def set_project(project):
    env.project = project


@task
def show_history(full=False):
    """ Cat the release history on remote hosts for the specified project. """
    require("project", provided_by=["set_project"])
    if full:
        run("cat {}".format(history_path(env.project)))
    else:
        run("tail -n 3 {}".format(history_path(env.project)))
    print current()


@task
def set_release(name):
    """ Finds the commit ID mapping to 'name' which can be a branch name, a
        commit ID or None in which case it defaults to HEAD. Sets env.commit
        which is used by, amongst others, push_release.
    """
    if name:
        env.commit = commit_by_name(name)
    else:
        env.commit = last_commit()


@task
def current(project_root='/srv'):
    """ Return release ID (SHA) of the current release for the project """
    require("project", provided_by=["set_project"])
    current_path = os.path.join(
        project_root, env.project, "releases", "current")

    current_release = run('readlink {}'.format(current_path))
    current_release_id = os.path.split(current_release)[-1]

    return current_release_id


@task
def push_release():
    """ Deploy commit identified by set_release previously.
        The release is not set live - the 'current' point is not amended -
        until a rollforward is done. The latter is a fast operation whilst this
        is slow.
    """
    require("commit", provided_by=["set_release"])
    require("project", provided_by=["set_project"])
    zipfile, _ = create_archive(env.project, env.commit)
    zfname = os.path.split(zipfile)[-1]

    # based on whether the archive is on the remote system or not, push our
    # archive
    target_file = "/srv/%s/packages/%s" % (env.project, zfname)
    if not exists(target_file):
        sudo("mkdir -p /srv/%s/packages/" % env.project)
        put(zipfile, target_file, use_sudo=True)
        sudo("cd /; tar zxf %s" % target_file)

    register_release(project_root='/srv',
                     project=env.project,
                     release=env.commit)

    if getattr(env, "install_requirements", True):
        if getattr(env, "pip_upgrade", False):
            upgrade_flag = "--upgrade"
        else:
            upgrade_flag = ""

        if getattr(env, "pip_quiet", False):
            quiet_flag = "--quiet"
        else:
            quiet_flag = ""
        sudo("%s ; pip install %s -r requirements.txt %s" %
            (activate_command(), upgrade_flag, quiet_flag))


@task
def prune_releases(releases='4'):
    """ Orders the project directory and then will keep the number of specified
        releases and delete any previous releases present to minimise the disk
        space.

        Arguments:

            releases (str): a string representation of the number of releases
                            to be left.
    """
    releases = int(releases)  # fabric params always come through as strings
    require("project", provided_by=["set_project"])
    release_list = get_releases('/srv', env.project)
    current_release = current()
    index = release_list.index(current_release)
    if index > releases:
        delete_release_list = release_list[:index-releases]
        for release in delete_release_list:
            purge('/srv', env.project, release)


@task
def purge_local_package(package):
    """ Purge a pip installed package from a project virtualenv. """
    require("project", provided_by=["set_project"])
    sudo("{0} ; yes y | /srv/{1}/bin/pip uninstall {2}".format(
        activate_command(), env.project, package))


@task
def purge_release():
    """ USE WITH CARE! This removes:

            * the package file from local cache
            * the package file from the remote package cache
            * the unpacked directory will be removed as long as it is not the
              current release.
    """
    require("commit", provided_by=["set_release"])
    require("project", provided_by=["set_project"])

    purge('/srv', env.project, env.commit)


@task
def rollback():
    """ Roll back a release to the previous, if available """
    require("project", provided_by=["set_project"])
    roll_history(env.project, PREVIOUS)


@task
def rollforward():
    """ Roll forward a release to a newer one, if available """
    require("project", provided_by=["set_project"])
    roll_history(env.project, NEXT)


