#!/usr/bin/env python
"""
forge.forge
~~~~~

:copyright: (c) 2010-2013 by Luis Morales
:license: BSD, see LICENSE for more details.
"""

#heavely based on diamond https://github.com/BrightcoveOS/Diamond

import os
import sys
import argparse
import logging
import traceback
import inspect

from util import load_class_from_name

from module import Module


class Forge(object):
    """
    Forge class loads and starts modules
    """
    pass

    def __init__(self, user, path, modules):
        # Initialize Logging
        self.log = logging.getLogger('forge')
        # Initialize Members
        self.modules = modules
        self.user = user
        self.path = path

    def load_include_path(self, path):
        """
        Scan for and add paths to the include path
        """
        # Verify the path is valid
        if not os.path.isdir(path):
            return
            # Add path to the system path
        sys.path.append(path)
        # Load all the files in path
        for f in os.listdir(path):
            # Are we a directory? If so process down the tree
            fpath = os.path.join(path, f)
            if os.path.isdir(fpath):
                self.load_include_path(fpath)

    def load_module(self, fqcn):
        """
        Load Module class named fqcn
        """
        # Load class
        cls = load_class_from_name(fqcn)
        # Check if cls is subclass of Module
        if cls == Module or not issubclass(cls, Module):
            raise TypeError("%s is not a valid Module" % fqcn)
            # Log
        self.log.debug("Loaded Module: %s", fqcn)
        return cls

    def load_modules(self, path):
        """
        Scan for collectors to load from path
        """
        # Initialize return value
        modules = {}

        # Get a list of files in the directory, if the directory exists
        if not os.path.exists(path):
            raise OSError("Directory does not exist: %s" % path)

        if path.endswith('tests') or path.endswith('fixtures'):
            return modules

        # Log
        self.log.debug("Loading Modules from: %s", path)

        # Load all the files in path
        for f in os.listdir(path):

            # Are we a directory? If so process down the tree
            fpath = os.path.join(path, f)
            if os.path.isdir(fpath):
                submodules = self.load_modules(fpath)
                for key in submodules:
                    modules[key] = submodules[key]

            # Ignore anything that isn't a .py file
            elif (os.path.isfile(fpath)
                  and len(f) > 3
                  and f[-3:] == '.py'
                  and f[0:4] != 'test'
                  and f[0] != '.'):

                modname = f[:-3]

                try:
                    # Import the module
                    mod = __import__(modname, globals(), locals(), ['*'])
                except ImportError:
                    # Log error
                    self.log.error("Failed to import module: %s. %s", modname, traceback.format_exc())
                    continue

                # Log
                self.log.debug("Loaded Module: %s", modname)

                # Find all classes defined in the module
                for attrname in dir(mod):
                    attr = getattr(mod, attrname)
                    # Only attempt to load classes that are infact classes
                    # are Collectors but are not the base Collector class
                    if (inspect.isclass(attr) and issubclass(attr, Module) and attr != Module):
                        # Get class name
                        fqcn = '.'.join([modname, attrname])
                        try:
                            # Load Collector class
                            cls = self.load_module(fqcn)
                            # Add Collector class
                            modules[cls.__name__] = cls
                        except Exception:
                            # Log error
                            self.log.error("Failed to load Module: %s. %s", fqcn, traceback.format_exc())
                            continue

        # Return Collector classes
        return modules

    def init_module(self, cls):
        """
        Initialize module
        """
        module = None
        try:
            # Initialize module
            module = cls(self.user)
            # Log
            self.log.debug("Initialized Module: %s", cls.__name__)
        except Exception:
            # Log error
            self.log.error("Failed to initialize Module: %s. %s", cls.__name__, traceback.format_exc())

        # Return module
        return module

    def run(self):
        """
        Load module classes and run them
        """

        # Load collectors
        modules_path = self.path
        self.load_include_path(modules_path)
        modules = self.load_modules(modules_path)

        for module in self.modules:
            c = self.init_module(modules[module.capitalize()])
            c.execute()


def run():
    """
    executes the recipe list to set the system
    """

    parser = argparse.ArgumentParser(
        prog='forge',
        description='forge is a command line tool that allows to execute modules to configure a linux system.',
        epilog='this epilog whose whitespace will be cleaned up and whose words will be wrapped across a couple lines'
    )

    parser.add_argument('-u', '--user', help='Destination user', type=str, required=True)
    parser.add_argument('-m', '--modules', help='List of modules to execute', nargs='+', type=str, required=True)
    parser.add_argument('-p', '--path', help='path to find modules', type=str, required=True)

    args = parser.parse_args()

    init = Forge(args.user, args.path, args.modules)
    init.run()
