'''
	pyject.make_dir.py
'''
import os
from root import ROOT_DIR

def add_package(projectName,packageName):
    dir = os.path.join(ROOT_DIR,projectName,projectName,packageName)
    os.makedirs(dir)
    init = os.path.join(dir,'__init__.py')
    os.system('touch ' + str(init))
    print 'Added package {} to project {}'.format(packageName,projectName)
