#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Leip
"""

import argparse
from collections import defaultdict
import hashlib
import logging
import importlib
import os
import pkg_resources
import sys
import textwrap

import Yaco

logging.basicConfig()
lg = logging.getLogger(__name__)
#lg.setLevel(logging.DEBUG)


#cache config files
CONFIG = {}


def get_config(name, config_files=None):

    global CONFIG

    if config_files is None:
        config_files = [
            'pkg://{}/etc/*.config'.format(name),
            sys.argv[0] + '.config',
            '/etc/{0}/'.format(name)]

    md5 = hashlib.md5()
    md5.update(name)
    md5.update(str(config_files))
    config_digest = md5.hexdigest()

    if CONFIG.has_key(config_digest):
        lg.debug("returning digest from CONFIG cache ({}) ({})".format(config_digest, name))
        return CONFIG[config_digest]

    new_config = Yaco.PolyYaco(name, files=config_files)
    CONFIG[config_digest] = new_config
    return new_config


class app(object):

    def __init__(self, name=None,
                 config_files = None,
                 set_name = 'set'):
        """

        :param name: base name of the applications
        :type name: string
        :param config_files: list of configuration files, if ommitted
             the app defaults to `/etc/<NAME>.yaml` and
             `~/.config/<NAME>/config.yaml`. The order is important, the last
             config file is the one to which changes will be saved
        :type config_files: a list of tuples: (id, filename)
        :param set_name: name of the command to set new values,
           if set to None, no set function is available. Default='set'
        :type set_name: string

        """

        if name is None:
            name = os.path.basename(sys.argv[0])
        self.name = name

        lg.debug("Starting Leip app")
        self.leip_commands = {}
        self.plugins = {}

        self.hooks = defaultdict(list)

        self.parser = argparse.ArgumentParser()

        self.parser.add_argument('-v', '--verbose', action='store_true')

        self.subparser = self.parser.add_subparsers(
            title = 'command', dest='command',
            help='"{}" command to execute'.format(name))

        #contains transient data - execution specific
        self.trans = Yaco.Yaco()

        #contains configuration data
        self.conf = get_config(self.name,
                               config_files=config_files)

        #create a 'set' command to manipulate the configuration
        def _conf_set(app, args):
            """
            Set & save a configuration value
            """
            self.conf[args.key] = args.value
            self.conf.save()

        #annotate the function for later use as command
        if not set_name is None:
            _conf_set._leip_command = set_name
            _conf_set._leip_args = [
                [['key'], {'help' : "key to set"}],
                [['value'], {'help' : "value to set the key to"}],
                ]
            self.register_command(_conf_set)

        #check for plugins
        if 'plugin' in self.conf:
            for plugin_name in self.conf.plugin:
                lg.debug("loading plugin %s" % plugin_name)

                module_name = self.conf.plugin[plugin_name].module.strip()

                enabled = self.conf.plugin[plugin_name].get('enabled', True)
                if not enabled:
                    continue


                lg.debug("attempting to load plugin from module {0}".format(
                    module_name))
                mod = importlib.import_module(module_name)

                self.plugins[plugin_name] = mod
                self.discover(mod)


        #register command run as a hook
        def _run_command(app):
            command = self.trans.args.command
            if command is None:
                self.parser.print_help()
                sys.exit(0)

            self.leip_commands[command](self, self.trans.args)
        self.register_hook('run', 50, _run_command)

        #register parse arguments as a hook
        def _prep_args(app):
            self.trans.args = self.parser.parse_args()
            if self.trans.args.verbose:
                rootlogger = logging.getLogger()
                rootlogger.setLevel(logging.DEBUG)

        self.register_hook('prepare', 50, _prep_args)

        #hook run order
        self.hook_order = ['prepare', 'run', 'finish']


    def discover(self, mod):
        """
        discover all hooks & commands in the provided module or
        module namespace (globals())

        :param mod: an imported module or a globals dict
        """

        if isinstance(mod, dict):
            mod_objects = mod
        else:
            mod_objects = mod.__dict__

        self.run_init_hook(mod_objects)
        self.discover_2(mod_objects)

    def run_init_hook(self, mod_objects):
        """
        Run prediscovery initialization hook for this module.

        This might allow, for example, flexible creation of functions
        to be discovered later on.

        For a hook to be executed as a prediscovery init hook, it needs to be
        decorated with: ''@leip.init''
        """

        leip_init_hook = None
        for obj_name in mod_objects:
            obj = mod_objects[obj_name]

            if isinstance(obj, Yaco.Yaco):
                continue

            #see if this is a function decorated as hook
            if hasattr(obj, '__call__') and \
                    hasattr(obj, '_leip_init_hook'):
                leip_init_hook = obj

        if not leip_init_hook is None:
            # execute init_hook - with the app - so
            # the module has access to configuration
            leip_init_hook(self)

    def discover_2(self, mod_objects):
        """
        Execute actual discovery of leip tagged functions & hooks
        """
        for obj_name in mod_objects:
            obj = mod_objects[obj_name]

            if isinstance(obj, Yaco.Yaco):
                continue

            #see if this is a function decorated as hook
            if not hasattr(obj, '__call__'):
                continue

            if hasattr(obj, '_leip_hook'):
                hook = obj._leip_hook
                if isinstance(hook, Yaco.Yaco):
                    continue
                prio = obj.__dict__.get('_leip_hook_priority', 100)
                lg.debug("discovered hook %s (%d) in %s" % (
                        hook, prio, obj.__name__))
                self.hooks[hook].append(
                    (prio, obj))

            if hasattr(obj, '_leip_command'):
                self.register_command(obj)

    def register_command(self, function):
        cname = function._leip_command
        lg.debug("discovered command %s" % cname)

        self.leip_commands[cname] = function

        #create a help text from the docstring - if possible
        _desc = [cname]
        if function.__doc__:
            _desc = function.__doc__.strip().split("\n", 1)

        if len(_desc) == 2:
            short_description, long_description = _desc
        else:
            short_description, long_description = _desc[0], ""

        long_description = textwrap.dedent(long_description)

        cp = self.subparser.add_parser(cname, help=short_description,
                                       description=long_description)

        for args, kwargs in function._leip_args:
            cp.add_argument(*args, **kwargs)

        function._cparser = cp

    def register_hook(self, name, priority, function):
        lg.debug("registering hook {0} / {1}".format(name, function))
        self.hooks[name].append(
            (priority, function))

    def run_hook(self, name, *args, **kw):
        """
        Execute hook
        """
        to_run = sorted(self.hooks[name])
        lg.debug("running hook %s" % name)

        for priority, func in to_run:
            lg.debug("running hook %s" % func)
            func(self, *args, **kw)

    def run(self):
        for hook in self.hook_order:
            self.run_hook(hook)


##
## Command decorators
##
def command(f):
    """
    Tag a function to become a command - take the function name and
    use it as the name of the command.
    """
    f._leip_command = f.__name__
    f._leip_args = []
    lg.debug("marking function as leip command: %s" % f.__name__)
    return f


def commandName(name):
    """
    as command, but provide a specific name
    """
    def decorator(f):
        lg.debug("marking function as leip command: %s" % name)
        f._leip_command = name
        f._leip_args = []
        return f
    return decorator


def arg(*args, **kwargs):
    """
    add an argument to a command - use the full argparse syntax
    """
    def decorator(f):
        lg.debug("adding leip argument {0}, {1}".format(str(args), str(kwargs)))
        f._leip_args.append((args, kwargs))
        return f
    return decorator


def flag(self, *args, **kwargs):
    """
    Add a flag to (default false - true if specified) any command
    """
    def decorator(f):
        kwargs['action'] = kwargs.get('action', 'store_true')
        kwargs['default'] = kwargs.get('default', False)
        f._cparser.add_argument(*args, **kwargs)
        return f
    return decorator


##
## Pre discovery init hook decorators
##
def init(f):
    """
    Mark this function as a pre discovery init hook.get_config.

    Only one per module is expected.
    """
    f._leip_init_hook = f.__name__
    return f


##
## Hook decorators
##
def hook(name, priority=50):
    """
    mark this function as a hook for later execution

    :param name: name of the hook to call
    :type name: string
    :param priority: inidicate how soon this hook must be called.
        Lower means sooner (default: 50)
    :type priority: int
    """
    def _hook(f):
        lg.debug("registering '%s' hook in %s priority %d" % (
                name, f.__name__, priority))
        f._leip_hook = name
        f._leip_hook_priority = priority
        return f

    return _hook





