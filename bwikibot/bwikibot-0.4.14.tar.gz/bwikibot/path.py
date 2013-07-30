import os

import appdirs

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

DATA_DIR = appdirs.user_data_dir('bwikibot')
ensure_dir(DATA_DIR)

def data_file(name):
    return os.path.join(DATA_DIR, name)


SESSION_FILE = data_file('cli.session')
SECONDARY_SESSION_FILE = data_file('cli_secondary.session')

