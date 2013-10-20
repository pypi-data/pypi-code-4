'''
	pyject.projects.py
'''
from make_file import make_setup_file, make_manifest, make_readme, make_init
from root import go_to_root
import sys
import os

def create_project(projectName):
    oldDir = os.getcwd()
    go_to_root()
    print 'Creating a new project named {}'.format(projectName)
    if os.path.exists(projectName):
        print 'Error: {} project dir already exists'.format(projectName)
        sys.exit(1)
    else:
        if not os.path.exists(projectName):
            os.mkdir(projectName)
        os.chdir(projectName)
        make_setup_file(projectName)
        make_manifest()
        make_readme()
        os.mkdir('tests')
        os.chdir('tests')
        make_init()
        os.chdir(os.pardir)
            if not os.path.exists(projectName):
                os.mkdir(projectName)
        os.chdir(projectName)
        make_init()
        os.chdir(oldDir)



