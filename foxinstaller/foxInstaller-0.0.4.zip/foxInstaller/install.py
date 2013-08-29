#!/usr/bin/python

import sys, os, platform

from subprocess import STDOUT, check_call
from optparse import OptionParser


# TODO: OPTION --noconfig: Dont ask for config changes from user.
# TODO: OPTION --yes: Skips confirmation prompts

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
        "nginx"
    ]
}

parser = OptionParser()

parser.add_option("-y", "--yes",
                  action="store_true", dest="ignore_prompts", default=False,
                  help="Dont ask for confirmations from user.")
parser.add_option("-q", "--no_config",
                  action="store_true", dest="no_config", default=False,
                  help="Dont ask for config from stdin.")


try:
    from cfg import basic_config
    
    config = config + basic_config
    
    print "* Loaded config from cfg.py... OK"
except ImportError:
    print "* No config found... FAIL"
    print "* Exiting..."
    sys.exit(0)

options, args = parser.parse_args()

def prompt(question, exit=True):
    if (options.ignore_prompts):
        return True

    val = raw_input("%s? (Y/N): " % question)
    if val.lower() != "y" and val.lower() != "yes":
        if exit:
            print "* Exiting..."
            sys.exit()
        return False
    return True

def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir, 0700)
        print "* Creating directory %s... OK" % dir
    else:
        print "* Searching for directory %s... OK" % dir

def get_install_dir():
    return config["INSTALL_DIR"] % config

def begin_install():
    print "-" * 55
    print "Begin %s Install" % config["PROJECT_NAME"]
    print "-" * 55
    
    if platform.system() != 'Windows':
        mkdir(get_install_dir())
    else:
        config["INSTALL_DIR"] = "."
    
    mkdir(os.path.join(get_install_dir(), 'log'))
    
    if platform.system() != 'Windows':
        print "* Running apt-get update... OK"
        check_call(['apt-get', 'update'], 
            stdout=open(os.devnull,'wb'), stderr=STDOUT)
        
        print "* Running apt-get install -y %s... OK" % ' '.join(config['PACKAGES'])
        check_call(['apt-get', 'install', '-y', ' '.join(config['PACKAGES'])], 
            stdout=open(os.devnull,'wb'), stderr=STDOUT)
    
    venv_bin = 'bin' if platform.system() != 'Windows' else 'Scripts'
    if not os.path.exists(os.path.join(get_install_dir(), config['VENV_DIR'], venv_bin, 'activate')):
        print "* Creating venv... OK"
        check_call(['virtualenv', '--system-site-packages', os.path.join(get_install_dir(), config['VENV_DIR'])], 
            stdout=open(os.devnull,'wb'), stderr=STDOUT)
    else:
        print "* Searching for venv... OK"

def update_script():
    unix = platform.system() != 'Windows'
    filename = os.path.join(get_install_dir(), 'update.sh' if unix else 'update.bat')
    
    comment = '#' if unix else 'REM'
    
    seq = [
        "%s %s Update script\r\n" % (comment, config["PROJECT_NAME"]),
    ]
    
    if unix:
        seq.append("service %s stop\r\n" % config["PROJECT_NAME"])
        seq.append(". ./%s/bin/activate\r\n" % config["VENV_DIR"])
    else:
        seq.append("cd %s/Scripts\r\n" % config["VENV_DIR"])
        seq.append("call activate.bat\r\n")
        seq.append("cd ../..\r\n")
    
    seq.append("cd %s\r\n" % config["PROJECT_NAME"])
    seq.append("python manage.py migrate\r\n")
    seq.append("python manage.py compilemessages\r\n")
    
    if unix:
        seq.append("service %s start\r\n" % config["PROJECT_NAME"])
    
    file = open(filename, 'w')
    file.writelines(seq)
    file.close()
    
    if unix:
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IEXEC)
    
    print "* Creating %s... OK" % filename

def main():
    print "Starting install script... OK"
    
    if options.no_config:
        print "Skipping user input"
    if options.ignore_prompts:
        print "Disabled prompts for inputs"
    
    needed = [
        "PROJECT_NAME",
        "VENV_DIR",
        "INSTALL_DIR",
        "USERNAME",
        "USERGROUP",
        "DOMAIN",
        "PORT"
    ]
    
    print "-" * 55
    print ""
    
    for key in needed:
        if options.ignore_prompts:
            val = None
        else:
            val = raw_input("Enter %s[%s]: " % (key, config.get(key, '')))
        config[key] = val if val else config.get(key, None)
        if not config[key]:
            print "* Get %s from standard input... FAIL" % key
            print "* Exiting..."
            sys.exit()
    
    print "-" * 55
    print "Loaded configuration: "
    
    for key in needed:
        print "\t%s: %s" % (key, config[key])
    
    print ""
    print "-" * 55
    
    prompt("Continue install process")
    
    begin_install()

    update_script()

if __name__ == "__main__":
    main()