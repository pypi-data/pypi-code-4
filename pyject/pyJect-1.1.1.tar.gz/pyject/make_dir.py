'''
	pyject.make_dir.py
'''
import os
from root import ROOT_DIR

def add_package(projectName,packageName,parent=None):
    if parent is None or parent == projectName:
        dir = os.path.join(ROOT_DIR,projectName,projectName,packageName)
    elif parent == 'root':
        dir = os.path.join(ROOT_DIR,projectName,packageName)
    else:
        dir = os.path.join(ROOT_DIR,projectName,parent)
    os.makedirs(dir)
    init = os.path.join(dir,'__init__.py')
    os.system('touch ' + str(init))
    print 'Added package {} to project {} '.format(packageName,projectName),
    if parent is not None and parent != 'root':
        print 'in package {}'.format(parent)
