# -*- coding: utf-8 -*-
# Copyright (c) 2013, Almar Klein
#
# This file is distributed under the terms of the (new) BSD License.

""" Module that serves as a proxy for loading PyQt4 libraries.

It loads either PySide or PyQt4 libraries and solves some
incompatibilities between them. Further, it allows using the PySide or
PyQt4 libraries of the system (the ones in /usr/lib/...), so that frozen
applications can look good. Of course this only works if the versions
are ABI compatible.

To use do ``from pyzolib.qt import QtCore, QtGui``. 

To give a preference for using pyside or PyQT4, set the ``QT_PREFER``
environment variable to "pyside" or "pyqt4". To prefer using the system
libraries, ``QT_PREFER`` should contain the string "system".

"""

import sys
import os
import imp
import importlib

qtPackage = None


class QtProxyImporter:
    """ Importer to import Qt modules, either from PySide or from PyQt,
    and either from this Python's version, or the system ones (if
    available and matching).
    """
    
    def find_module(self, fullname, path=None):
        """ This is called by Python's import mechanism. We return ourself
        only if this really looks like a Qt import, and when its imported
        as a submodule from this stub package.
        """
        
        # Get different parts of the module name
        nameparts = fullname.split('.') 
        basename = nameparts[0]
        modulename = nameparts[-1]
        
        if '.'.join(nameparts[:-1]) != __name__:
            return
        
        if modulename.startswith('Qt'):
            if qtPackage is None:
                self._import_qt()
            return self
    
    
    def load_module(self, fullname):
        """ This method is called by Python's import mechanism after
        this instance has been returned from find_module. Here we
        actually import the module and do some furher processing.
        """
        
        # Get different parts of the module name
        nameparts = fullname.split('.') 
        basename = nameparts[0]
        modulename = nameparts[-1]
        
        # Get real name and import, this yields the base package, also get mod
        # We also need to set sys.path in case this is a system package
        realmodulename = '%s.%s' % (qtPackage.__name__, modulename)
        qtdir = os.path.dirname(qtPackage.__file__)
        if os.path.isdir(qtdir):
            sys.path.insert(0, os.path.dirname(qtdir))
            try:
                for entry in os.listdir(qtdir):
                    if entry.startswith(modulename+'.'):
                        m = imp.load_dynamic(realmodulename, os.path.join(qtdir, entry))
                        break
                else:
                    raise ImportError('Could not import %s' % realmodulename)
            finally:
                sys.path.pop(0)
        else:
            p = __import__(realmodulename)
            m = getattr(p, modulename)
        
        # Also register in sys.modules under the name as it was imported
        sys.modules[realmodulename] = m
        sys.modules[fullname] = m
        
        # Fix some compatibility issues
        self._fix_compat(m)
        
        # Done
        return m
    
    
    def _import_qt(self, prefer=None):
        """ This is where we import either PySide or PyQt4.
        This is done only once.
        """
        if not prefer:
            prefer = os.environ.get('QT_PREFER', None)
        if not prefer:
            prefer = 'PySide'  # If all works well we might go and prefer system
        prefer = prefer.lower().strip()
        global qtPackage
        
        # Perhaps it is already loaded
        if 'PySide' in sys.modules:
            #global qtPackage
            qtPackage = sys.modules['PySide']
            return
        elif 'PyQt4' in sys.modules:
            #global qtPackage
            qtPackage = sys.modules['PyQt4']
            return
        
        # Init potential imports
        pyside_imports = [('PySide', None)]
        pyqt4_imports = [('PyQt4', None)]
        pyside_system_imports = []
        pyqt4_system_imports = []
        
        # Get possible paths, but only on Linux
        if sys.platform.startswith('linux'):
            # Determine where PySide or PyQt4 can be
            ver = sys.version[:3]
            possible_paths = ['/usr/local/lib/python%s/dist-packages' % ver,
                os.path.expanduser('~/.local/lib/python%s/site-packages' % ver)]
            if os.path.isdir('/usr/lib/python%s' % ver):
                possible_paths.append('/usr/lib/python%s/dist-packages' % ver[0])
            # Trty if it is there
            for path in possible_paths:
                if os.path.isdir(os.path.join(path, 'PySide')):
                    pyside_system_imports.append(('PySide', path))
                if os.path.isdir(os.path.join(path, 'PyQt4')):
                    pyqt4_system_imports.append(('PyQt4', path))
        
        # Combine imports in right order
        if prefer.startswith('system'):
            if 'pyside' in prefer:
                imports =   pyside_system_imports + pyqt4_system_imports + \
                            pyside_imports + pyqt4_imports
                            
            elif 'pyqt4' in prefer.lower():
                imports =   pyqt4_system_imports + pyside_system_imports + \
                            pyqt4_imports + pyside_imports
            else:
                print('Warning: invalid Qt preference given: "%s"' % prefer)
                imports =   pyside_system_imports + pyqt4_system_imports + \
                            pyside_imports + pyqt4_imports
        elif 'system' in prefer:
            if 'pyside' in prefer:
                imports =   pyside_system_imports + pyside_imports + \
                            pyqt4_system_imports + pyqt4_imports
            elif 'pyqt4' in prefer.lower():
                imports =   pyqt4_system_imports + pyqt4_imports + \
                            pyside_system_imports + pyside_imports
            else:
                print('Warning: invalid Qt preference given: "%s"' % prefer)
                imports =   pyside_system_imports + pyside_imports + \
                            pyqt4_system_imports + pyqt4_imports
        else:
            if 'pyside' in prefer:
                imports =   pyside_imports + pyqt4_imports + \
                            pyside_system_imports + pyqt4_system_imports
            elif 'pyqt4' in prefer.lower():
                imports =   pyqt4_imports + pyside_imports + \
                            pyqt4_system_imports + pyside_system_imports
            else:
                print('Warning: invalid Qt preference given: "%s"' % prefer)
                imports =   pyside_imports + pyqt4_imports + \
                            pyside_system_imports + pyqt4_system_imports 
        
        # Try importing
        package = None
        for package_name, path in imports:
            if path:
                sys.path.insert(0, path)
            try:
                package = __import__(package_name, level=0)
                break
            except ImportError:
                pass
            finally:
                if path:
                    sys.path.pop(0)
        
        # Store package or raise import error
        if package:
            qtPackage = package
        else:
            raise ImportError('Could not import PySide nor PyQt4.')
    
    
    def _fix_compat(self, m):
        """ Fix incompatibilities between PySide and PyQt4. 
        """
        #print('fix', m.__name__)
        if qtPackage.__name__ == 'PySide':
            pass
        else:
            if m.__name__ == 'QtCore':
                QtCore.Signal = QtCore.pyqtSignal
        
        # todo: more compat, like uic loading


sys.meta_path.insert(0, QtProxyImporter())
