#!/usr/bin/python

import sys, os

from optparse import OptionParser


# TODO: OPTION --noconfig: Dont ask for config changes from user.
# TODO: OPTION --yes: Skips confirmation prompts

basic_config = {
    "PROJECT_NAME": None,
    "VENV_DIR": "venv",
    "INSTALL_DIR": "/srv/%(project_name)s",
    "USERNAME": None,
    "USERGROUP": None,
    "DOMAIN": None,
    "PORT": 8000,
}

try:
    from cfg import basic_config
    print "* Loaded config from cfg.py... OK"
except ImportError:
    print "* No config found... FAIL"
    print "* Exiting..."
    sys.exit(0)

parser = OptionParser()

parser.add_option("-y", "--yes",
                  action="store_true", dest="ignore_prompts", default=False,
                  help="Dont ask for confirmations from user.")
parser.add_option("-q", "--no_config",
                  action="store_true", dest="no_config", default=False,
                  help="Dont ask for config from stdin.")

def prompt(question):
    val = raw_input("%s? (Y/N): " % question)
    if val.lower() != "y" and val.lower() != "yes":
        print "* Exiting..."
        sys.exit()
    

def main():
    print "Starting install script... OK"
    
    options, args = parser.parse_args()
    
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
            val = raw_input("Enter %s[%s]: " % (key, basic_config.get(key, '')))
        basic_config[key] = val if val else basic_config.get(key, None)
        if not basic_config[key]:
            print "* Get %s from standard input... FAIL" % key
            print "* Exiting..."
            sys.exit()
    
    print "-" * 55
    print "Loaded configuration: "
    
    for key in needed:
        print "\t%s: %s" % (key, basic_config[key])
    
    print ""
    print "-" * 55
    
    prompt("Continue install process")

if __name__ == "__main__":
    main()