import os
import sys
if not os.getenv('ROOT'):
    os.environ['ROOT'] = os.path.expanduser('~') + os.sep + 'projects'

def get_env_root():
    if os.getenv('ROOT'):
        return os.environ['ROOT']
    else:
        print 'Error env ROOT not set!'

ROOT_DIR = get_env_root()

def check_root():
	if not os.path.exists(ROOT_DIR):
		os.makedirs(ROOT_DIR)

def go_to_root():
	check_root()
	os.chdir(ROOT_DIR)

def set_root(Dir):
    if os.path.exists(Dir):
        return Dir
    else:
        print 'Error! No root Dir'
