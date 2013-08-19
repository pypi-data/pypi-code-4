import os
import setuptools
import shutil
import sys
import tempfile
from zc.buildout.download import Download
import zc
import zc.recipe.egg

DOWNLOAD_URL = 'http://projects.unbit.it/downloads/uwsgi-latest.tar.gz'
EXCLUDE_OPTIONS = set([
        'bin-directory', 'develop-eggs-directory', 'eggs',
        'eggs-directory', 'executable', 'extra-paths', 'download-url',
        'find-links', 'python', 'recipe', 'pth-files'])

_oprp = getattr(os.path, 'realpath', lambda path: path)
def realpath(path):
    return os.path.normcase(os.path.abspath(_oprp(path)))

class UWSGI:
    """Buildout recipe downloading, compiling and configuring python
    paths for uWSGI.
    """

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.name = name
        self.buildout = buildout

        if 'extra-paths' in options:
            options['pythonpath'] = options['extra-paths']
        else:
            options.setdefault('extra-paths', options.get('pythonpath', ''))

        # Collect configuration params from options.
        self.conf = {}
        self.install_path = os.path.join(
            buildout['buildout']['bin-directory'], name)
        self.download_url = options.get('download-url', DOWNLOAD_URL)
        for key in options:
            # XXX: Excludes buildout fluff. This code sucks, there
            # must be a better way.
            if key in EXCLUDE_OPTIONS:
                continue
            elif key.startswith('_'):
                continue
            self.conf[key] = options.get(key, None)

        self.options = options

    def download_release(self):
        """Download uWSGI release based on 'version' option and return
        path to downloaded file.
        """
        cache = tempfile.mkdtemp('download-cache')
        download = Download(cache=cache)
        download_path, is_temp = download(self.download_url)
        return download_path

    def extract_release(self, download_path):
        """Extracts uWSGI package and returns path containing
        uwsgiconfig.py along with path to extraction root.
        """
        uwsgi_path = None
        extract_path = tempfile.mkdtemp("-uwsgi")
        setuptools.archive_util.unpack_archive(download_path, extract_path)
        for root, dirs, files in os.walk(extract_path):
            if 'uwsgiconfig.py' in files:
                uwsgi_path = root
        return uwsgi_path, extract_path

    def build_release(self, uwsgi_path):
        """Build uWSGI and returns path to executable.
        """
        # Change dir to uwsgi_path for compile.
        sys_path_changed = False
        current_path = os.getcwd()
        os.chdir(uwsgi_path)

        try:
            # Add uwsgi_path to the Python path so we can import uwsgiconfig.
            if uwsgi_path not in sys.path:
                sys.path.append(uwsgi_path)
                sys_path_changed = True

            # Build uWSGI.
            uwsgiconfig = __import__('uwsgiconfig')
            bconf = '%s/buildconf/default.ini' % uwsgi_path
            uconf = uwsgiconfig.uConf(bconf)
            uconf.set('bin_name', self.name)
            uwsgiconfig.build_uwsgi(uconf)
        finally:
            # Change back to original path and remove uwsgi_path from
            # Python path if added.
            os.chdir(current_path)
            if sys_path_changed:
                sys.path.remove(uwsgi_path)

        shutil.copy(os.path.join(uwsgi_path, self.name), self.install_path)

    def get_extra_paths(self):
        """Returns extra paths to include for uWSGI.
        """
        # Add libraries found by a site .pth files to our extra-paths.
        if 'pth-files' in self.options:
            import site
            for pth_file in self.options['pth-files'].splitlines():
                pth_libs = site.addsitedir(pth_file, set())
                if not pth_libs:
                    self.log.warning(
                        "No site *.pth libraries found for pth_file=%s" % (
                         pth_file,))
                else:
                    self.log.info("Adding *.pth libraries=%s" % pth_libs)
                    self.options['extra-paths'] += '\n' + '\n'.join(pth_libs)

        # Add local extra-paths.
        return [p.replace('/', os.path.sep) for p in
                self.options['extra-paths'].splitlines() if p.strip()]

    def create_conf_xml(self):
        """Create xml file file with which to run uwsgi.
        """
        path = os.path.join(
            self.buildout['buildout']['parts-directory'],
            self.name)
        if not os.path.isdir(path):
            os.makedirs(path)

        xml_path = os.path.join(path, 'uwsgi.xml')

        conf = ""
        for key, value in self.conf.items():
            if value.lower() in ('true', 'on', 'yes'):
                conf += "<%s/>\n" % key
            elif value and value.lower() not in ('false', 'off', 'yes'):
                conf += "<%s>%s</%s>\n" % (key, value, key)


        requirements, ws = self.egg.working_set()
        eggs_paths = [dist.location for dist in ws]
        eggs_paths.extend(self.get_extra_paths())
        # order preserving unique
        unique_egg_paths = []
        for p in eggs_paths:
            if p not in unique_egg_paths:
                unique_egg_paths.append(p)

        for path in map(realpath, unique_egg_paths):
            conf += "<pythonpath>%s</pythonpath>\n" % path

        f = open(xml_path, 'w')
        f.write("<uwsgi>\n%s</uwsgi>" % conf)
        f.close()
        return xml_path

    def install(self):
        paths = [self.install_path]
        if not os.path.isfile(self.install_path):
            # Download uWSGI.
            download_path = self.download_release()

            # Extract uWSGI.
            uwsgi_path, extract_path = self.extract_release(download_path)

            try:
                # Build uWSGI.
                self.build_release(uwsgi_path)
            finally:
                # Remove extracted uWSGI package.
                shutil.rmtree(extract_path)

        # Create uWSGI conf xml.
        paths.append(self.create_conf_xml())
        return paths

    update = install
