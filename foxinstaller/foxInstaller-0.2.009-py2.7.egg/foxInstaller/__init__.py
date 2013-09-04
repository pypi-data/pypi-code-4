#!/usr/bin/python

import sys, os, platform, stat

from contextlib import contextmanager
from subprocess import STDOUT, check_call, check_output, CalledProcessError, call
from optparse import OptionParser

from fox_file_templates import windows_templates, unix_templates

config = {
    "PROJECT_NAME": None,
    "VENV_DIR": "venv",
    "INSTALL_DIR": "/srv/%(PROJECT_NAME)s",
    "USERNAME": None,
    "USERGROUP": None,
    "DOMAIN": None,
    "PORT": 8000,

    "PACKAGES": [
        "python-setuptools",
        "python-virtualenv",
        "python-pip",
        "libjpeg-dev",
        "libpng-dev",
        "nginx",
        "git"
    ]
}

parser = OptionParser()

parser.add_option("-y", "--yes",
                  action="store_true", dest="ignore_prompts", default=False,
                  help="Dont ask for confirmations from user.")
parser.add_option("-q", "--no_config",
                  action="store_true", dest="no_config", default=False,
                  help="Dont ask for config from stdin.")
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="Verbose logging.")


try:
    from cfg import basic_config

    config = dict(config.items() + basic_config.items())

    print "* Loaded config from cfg.py... OK"
except ImportError:
    print "* No config found... FAIL"
    print "* Exiting..."
    sys.exit(0)

options, args = parser.parse_args()

class OSHelpers(object):

    @staticmethod
    def mkdir(theDir, flag=0700):
        if not os.path.exists(theDir):
            os.makedirs(theDir, flag)
            return True
        else:
            return False

    @staticmethod
    def chown_r(path, uid, gid):
        for root, dirs, files in os.walk(path):
            for theDir in dirs:
                os.chown(os.path.join(root, theDir), uid, gid)
            for fil in files:
                os.chown(os.path.join(root, fil), uid, gid)

    @staticmethod
    def chmod_r(path, mode):
        for root, dirs, files in os.walk(path):
            for theDir in dirs:
                os.chmod(os.path.join(root, theDir), mode)
            for theFile in files:
                os.chmod(os.path.join(root, theFile), mode)

    @staticmethod
    def chmod_x(filename):
        if os.path.exists(filename) and os.path.isfile(filename):
            st = os.stat(filename)
            os.chmod(filename, st.st_mode | stat.S_IEXEC)

class FoxInstaller(object):
    required = [
        "PROJECT_NAME",
        "VENV_DIR",
        "INSTALL_DIR",
        "USERNAME",
        "USERGROUP",
        "DOMAIN",
        "PORT"
    ]

    def __init__(self):
        self.config = {}
        self.verbose = False

    def load_config(self, cfg, no_input=False, no_promts=False, verbose=False):
        self.config = cfg
        self.no_input = no_input
        self.no_promts = no_promts
        self.verbose = verbose

        self.install_dir = self.config["INSTALL_DIR"] % self.config
        self.is_unix = platform.system() != 'Windows'

    def install(self):
        print "Starting install script..."

        if self.no_input:
            print "Skipping user input"
        if self.no_promts:
            print "Disabled confirmations"

        self.read_input()
        
        print "Platform: %s, %s" % ("UNIX" if self.is_unix else "WIN", platform.system())
        print "-" * 55
        
        self.prompt("Continue install process")
        

        with self.log_helper('Creating log dir'):
            OSHelpers.mkdir(os.path.join(self.install_dir, 'log'))

        self.apt_get()
        self.create_venv()
        self.create_files()

        self.chown_and_chmod()

        self.pull()
        self.dependencies()

        print "-" * 55
        print "ALL DONE"

    def read_input(self):
        print "-" * 55
        print ""

        for key in self.required:
            if self.no_input:
                val = None
            else:
                val = raw_input("Enter %s[%s]: " % (key, self.config.get(key, '')))
            self.config[key] = val if val else self.config.get(key, None)
            if not self.config[key]:
                print "* Get %s from standard input... FAIL" % key
                print "* Exiting..."
                sys.exit()

        print "-" * 55
        print "Loaded configuration: "

        for key in self.required:
            print "\t%s: %s" % (key, self.config[key])

        print ""
        print "-" * 55

    def apt_get(self):
        if self.is_unix:
            with self.log_helper('Running apt-get update'):
                check_call(['sudo', 'apt-get', 'update'], stdout=open(os.devnull,'wb'), stderr=STDOUT)

            for package in self.config['PACKAGES']:
                with self.log_helper('Running apt-get install -y %s' % package):
                    check_call(['sudo', 'apt-get', 'install', '-y', package], stdout=open(os.devnull,'wb'), stderr=STDOUT)

    def create_venv(self):
        venv_bin = 'bin' if self.is_unix else 'Scripts'

        if not os.path.exists(os.path.join(self.install_dir, self.config['VENV_DIR'], venv_bin, 'activate')):
            with self.log_helper('Creating venv'):
                check_call(['virtualenv', '--system-site-packages', os.path.join(self.install_dir, self.config['VENV_DIR'])],
                    stdout=open(os.devnull,'wb'), stderr=STDOUT)
        else:
            print "* Found venv."

    def create_files(self):
        with self.log_helper('Creating update script'):
            self.file_from_template('update.sh' if self.is_unix else 'update.bat', 'update', self.install_dir, True)

        with self.log_helper('Creating start script'):
            self.file_from_template('start.sh' if self.is_unix else 'start.bat', 'start', self.install_dir, True)

        with self.log_helper('Creating nginx conf'):
            self.file_from_template('%s.conf' % self.config["PROJECT_NAME"], 'nginx_conf', '/etc/nginx/conf.d/', True)

        with self.log_helper('Creating upstart job'):
            self.file_from_template('%s.conf' % self.config["PROJECT_NAME"], 'upstart_job', '/etc/init/', True)

    def chown_and_chmod(self):
        if self.is_unix:
            with self.log_helper('Changing user permissions'):
                import pwd, grp

                uid = pwd.getpwnam(self.config['USERNAME']).pw_uid
                gid = grp.getgrnam(self.config['USERGROUP']).gr_gid

                OSHelpers.chown_r(self.install_dir, uid, gid)
                OSHelpers.chmod_r(self.install_dir, 0700)

    def pull(self):
        with self.log_helper('Pulling from server'):
            check_output(['git', 'pull'], stderr=STDOUT)

    def dependencies(self):
        with self.log_helper('Installing dependencies'):
            if self.is_unix:
                cmd = 'source %(INSTALL_DIR)s/%(VENV_DIR)s/bin/activate && pip install -r requirements.txt'
            else:
                cmd = 'cd %(VENV_DIR)s/Scripts & call activate.bat & cd ..\.. & pip install -r requirements.txt'

            cmd = cmd % dict(self.config.items() + {"INSTALL_DIR": self.install_dir}.items())
            
            if self.verbose:
                os.system(cmd)
            else:
                with open(os.devnull, "w") as fnull:
                    call(cmd, stdout = fnull, stderr = fnull)

    def syncdb(self):
        with self.log_helper('Installing dependencies'):
            if self.is_unix:
                cmd = "source %(INSTALL_DIR)s/%(VENV_DIR)s/bin/activate && cd %(PROJECT_NAME)s && python manage.py syncdb"
            else:
                cmd = 'cmd.exe /K "cd %(VENV_DIR)s/Scripts & call activate.bat & cd ..\\..\\%(PROJECT_NAME)s & python manage.py syncdb'

            cmd = cmd % dict(self.config.items() + {"INSTALL_DIR": self.install_dir}.items())
            check_call([cmd], stdout=open(os.devnull,'wb'), stderr=STDOUT)

    # Helpers

    @contextmanager
    def log_helper(self, action):
        sys.stdout.write("* %s... " % action)
        try:
            yield
            print "OK"
        except CalledProcessError, e:
            print "FAIL"
            if self.verbose:
                print "Exception: ", e, e.output
        except Exception, e:
            print "FAIL"
            if self.verbose:
                print "Exception: ", e

    def file_from_template(self, filename, tpl_name, base_dir='', executable=False):
        if base_dir:
            filename = os.path.join(base_dir, filename)

        if not self.is_unix:
            tpl_container = windows_templates
        else:
            tpl_container = unix_templates

        if tpl_name in tpl_container:

            data = tpl_container[tpl_name] % dict(self.config.items() + {"INSTALL_DIR": self.install_dir}.items())

            theFile = open(filename, 'w')
            theFile.write(data)
            theFile.close()

            if self.is_unix and executable:
                OSHelpers.chmod_x(filename)

    def prompt(self, question, close=True):
        if self.no_promts:
            return True

        val = raw_input("%s? (Y/N): " % question)
        if val.lower() != "y" and val.lower() != "yes":
            if close:
                print "* Exiting..."
                sys.exit()
            return False
        return True

inst = FoxInstaller()
inst.load_config(config, no_input=options.no_config, no_promts=options.ignore_prompts, verbose=options.verbose)
inst.install()