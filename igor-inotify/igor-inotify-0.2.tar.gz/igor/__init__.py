#!/usr/bin/env python
"""Igor: start/stop and manage containers in response to filesystem events
"""

__author__ = "Da_Blitz"
__version__ = "0.2"
__email__ = "code@pocketnix.org"
__license__ = "BSD (3 Clause)"
__url__ = "http://code.pocketnix.org/igor"

from argparse import ArgumentParser, FileType
from butter.inotify import Inotify
from yaml import safe_load as load
from collections import namedtuple
from consts import get_setting
from imp import load_source
import logging
import select
import consts
import sys
import os

APP_NAME = consts.defaults['APP_NAME']
log = logging.getLogger(APP_NAME)

# Note we have to open inotify and add the watches BEFORE
# we process what is already on the FS to ensure we dont 
# lose any events. make sure all operations are idepotent
# as its possible to read from the directory somthing that
# will be signalled from inotify
Plugin = namedtuple("Plugin", 'filename func settings')


class EventDispatcher(object):
    def __init__(self):
        self._events = {}
        self._default = lambda x: None
    
    def __getitem__(self, key):
        return self._events[key]
        
    def __setitem__(self, key, val):
        self._events[key] = val
        
    def __delitem__(self, key):
        del self._events[key]
        
    def register(self, events=None, *args, **kwargs):
        def inner(func):
            if events is not None:
                for event in events:
                    self._events[event] = func
            else:
                self._default = func
            return func
        return inner
        
    def __call__(self, event):
        self._events.get(event.mask, self._default)(event)


class Loop(object):
    def __init__(self):
        self._notifiers = {}
        self._selector = select.epoll()
    
    def get_inotify(self, name, callback):
        i = Inotify()
        fd = i.fileno()
        self._notifiers[fd] = (name, i, callback)
        self._selector.register(fd)
        
        return i
        
    def loop(self, timeout=-1):
        for fd, mask in self._selector.poll(timeout):
            name, i, callback = self._notifiers[fd]
            events = i.read_events()
            for event in events:
                try:
                    callback(event)
                except Exception as err:
                    log.exception('%s generated an exception on filesystem event: %s', name, event)
        
    def loop_forever(self):
        while True:
            self.loop()
            
def read_daemon_config(config_path):
    log.info("Reading config file: %s", config_path)
    try:
        with open(config_path) as file:
            config = load(file)
    except (OSError, IOError):
        log.info("Could not open config file: %s", config_path)
        config = {}
        
    return config

def read_plugin_configs(config_dir):
    log.info("Reading plugin configs from: %s", config_dir)
    try:
        dir = os.listdir(config_dir)
    except OSError:
        dir = []
    configs = [conf for conf in dir if conf.endswith('.conf')]
    configs = [os.path.join(config_dir, conf) for conf in configs]
    log.info("Found configs: %s", ", ".join(configs))
    
    plugins = []
    for config in configs:
        log.info("Reading config: %s", config)
        try:
            with open(config) as conf:
                plugin_conf = load(conf) or {}
            
            for option in ['plugin', 'name']:
                if option not in plugin_conf:
                    raise ValueError(option)
            
            plugin_path = plugin_conf['plugin']
            filename, func = split_plugin_path(plugin_path)
            
            plugin = Plugin(filename, func, plugin_conf)
            plugins.append(plugin)
        except (IOError, OSError):
            log.error("Could not open config file: %s", config)
        except ValueError, err:
            log.error('Could not load config: %s, missing key "%s"', config, err.args[0])
    
    return plugins


def split_plugin_path(path, default_func="setup"):
    """given a path to a module in the form "/path/to/module.py:function"
    return a 2 element list containg the path to the file and the fucntion 
    to call in that file
    
    >>> split_plugin_path("/path/to/module.py:function")
    ["/path/to/module.py", "function"]
    """
    ret = path.split(":", 1) + [default_func]
    ret = ret[:2]
    
    return ret


def setup_plugin(base_dir, plugin, logger, get_inotify):
    """Given a path to a loadable module and function to call in that file,
    load the plugin and call it with the supplied arguments
    """
    file = os.path.join(base_dir, plugin.filename)
    name = "plugin:{}".format(plugin.filename)
    
    module = load_source(name, file)

    setup = getattr(module, plugin.func)
    setup(plugin.settings, logger, get_inotify)

    return module

def main(argv=sys.argv[1:]):
    args = ArgumentParser()
    args.add_argument("-c", "--config", type=FileType("r"),
                      help="Main config file to read settings from")
    args.add_argument("-v", "--verbose", action="count", dest="log_level", default=0,
                      help="Increase the verbosity of logging, can be specified multiple times")
    options = args.parse_args(argv)
    
    level = { 0:logging.CRITICAL,
              1:logging.ERROR,
              2:logging.WARN,
              3:logging.INFO,
              4:logging.DEBUG,
             }.get(min(options.log_level, 4), 0)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)-8s:%(asctime)s:%(name)s: %(message)s")
    handler.setFormatter(formatter)
    log.setLevel(level)
    log.addHandler(handler)
    
    config = get_setting("CONFIG", options.config, None)
    config = read_daemon_config(config)
    config_dir = get_setting('CONFIG_DIR', None, config.get('config_dir'))
    plugins = read_plugin_configs(config_dir)
    
    manager = Loop()
    for plugin in plugins:
        name = plugin.settings['name']
        log.info("Setting up plugin: %s", name)
        logger = logging.getLogger("{}.plugins.{}".format(APP_NAME, name))
        from functools import partial
        get_inotify = partial(manager.get_inotify, name)
        try:
            setup_plugin(config_dir, plugin, logger, get_inotify)
        except Exception as Err:
            log.exception("Uncaught error during setup, not loading module")

    log.info("Entering main loop")
    try:
        manager.loop_forever()
    except KeyboardInterrupt:
        print "User requested exit"

if __name__ == "__main__":
    main()
