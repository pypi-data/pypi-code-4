'''
	pyject.make_file.py
'''
import os
import sys
from make_text import make_main, make_test, make_setup
from root import go_to_root

types = {
    'main': make_main,
    'test': make_test,
    'setup': make_setup,
    }

def add_module(projectName,moduleName,packageName=None):
    print 'adding module named {} to project {}'.format(moduleName,projectName)
    oldDir = os.getcwd()
    go_to_root()
    if not os.path.exists(projectName):
        print 'Error: {} project dir does not exist'
        sys.exit(1)
    
    os.chdir(projectName)
    if packageName is not None:
        f = os.path.join(projectName,packageName,moduleName)
    else:
        f = os.path.join(projectName,moduleName)
    make_main_file(f)

    if os.path.exists(moduleName):
        print 'made python module {}'.format(moduleName)
        os.chdir(oldDir)
    else:
        sys.exit(1)
    
def make_file(fileName, txt=None):
    if os.path.exists(fileName):
        print 'Error: {} already exists!'.format(fileName)
        sys.exit(1)
    else:
        try:
            if not fileName.endswith('.py'):
                    fileName += '.py'
            f = open(fileName,'w')
            if txt is not None:
                f.write(txt)
        except Exception:
            print 'File Error!'
        finally:
            f.close()

def get_text(name, fileType):
    return types[fileType](name)

def make_setup_file(projName):
    make_file('setup.py',get_text(projName,'setup'))

def make_main_file(projName):
    make_file(projName,get_text(projName,'main'))

def make_test_file(projName):
    make_file('test.py',get_text(projName,'test'))

def make_init():
    make_file('__init__.py')

def make_manifest():
    make_file('MANIFEST.in')

def make_readme(txt=None):
    make_file('README',txt)


