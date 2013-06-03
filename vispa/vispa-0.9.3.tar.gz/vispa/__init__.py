# -*- coding: utf-8 -*-

import os
import sys
import traceback
import re
import socket
import logging
import csv
import token
import tokenize
from StringIO import StringIO
import pkgutil
import importlib
import inspect
import vispa.extensions

try:
    import ConfigParser as cp
except:
    import configparser as cp

logger = logging.getLogger(__name__)

_datapath = 'data'
_configpath = 'conf'
_codepath = os.path.split(__path__[0])[0]

def datapath(*args):
    return os.path.join(_datapath, *args)

def set_datapath(p):
    global _datapath
    _datapath = p

def configpath(*args):
    return os.path.join(_configpath, *args)

def set_configpath(p):
    global _configpath
    _configpath = os.path.abspath(p)

def codepath(*args):
    return os.path.join(_codepath, *args)

def set_codepath(p):
    global _codepath
    _codepath = p

class _ConfigParser(cp.SafeConfigParser):
    def __call__(self, section, option, default=None):
        if config.has_option(section, option):
            value = config.get(section, option)
            # try to cast according to 'default'
            if default is None:
                return value
            # string
            if isinstance(default, str):
                return str(value)
            # list
            elif isinstance(default, list):
                l = []
                g = tokenize.generate_tokens(StringIO(value).readline)
                for toknum, tokval, _, _, _  in g:
                    if toknum == token.NAME or toknum == token.NUMBER:
                        l.append(tokval)
                    elif toknum == token.STRING:
                        l.append(tokval[1:-1])
                return l

            # tuple
            elif isinstance(default, tuple):
                if len(value):
                    return tuple(value.split(','))
                else:
                    return ()
            # boolean
            elif isinstance(default, bool):
                if value == 'True':
                    return True
                elif value == 'False':
                    return False
            # TODO: dict
            else:
                return value
        else:
            return default

# setup a config parser for "vispa.ini"
config = _ConfigParser()

# a little publish/subscribe system
_callbacks = {}

def subscribe(topic, callback):
    if callback not in _callbacks.get(topic, []):
        _callbacks.setdefault(topic, []).append(callback)
register_callback = subscribe

def publish(topic, *args, **kwargs):
    values = []
    for callback in _callbacks.get(topic, []):
        try:
            value = callback(*args, **kwargs)
            values.append(value)
        except Exception:
            values.append(None)
            log_exception()
    return values
fire_callback = publish

def exception_string():
    exc_type, exc_value, exc_tb = sys.exc_info()
    st = traceback.format_exception(exc_type, exc_value, exc_tb)
    return  ''.join(st)

def log_exception():
    sys.stderr.write(exception_string())

class Netstat(object):

    #                                       13:      0100007F:BBD6             0100007F:AF83            01             00000000:00000000               00:00000000       00000000  1000        0 111481 1 ffff8801b650d400 20 0 0 10 -1                    
    _proc_net_tcp_re = re.compile('\W+([0-9]+):\W+([0-9A-F]+):([0-9A-F]+)\W+([0-9A-F]+):([0-9A-F]+)\W+([0-9A-F]+)\W+([0-9A-F]+):([0-9A-F]+)\W+([0-9A-F]+):([0-9A-Z]+)\W+([0-9A-F]+)\W+([0-9A-F]+)\W+([0-9A-F]+).*')

    IDX_LOCAL_IP = 2
    IDX_LOCAL_PORT = 3
    IDX_REMOTE_IP = 4
    IDX_REMOTE_PORT = 5
    IDX_USERID = 12

    @staticmethod
    def ipv4_to_hex(ip):
        parts = ip.split(".")
        parts.reverse()
        return "".join(["%02X" % int(part) for part in parts])

    @staticmethod
    def port_to_hex(port):
        return "%02X" % port
    
    @staticmethod
    def get_socket_owner_file(filename, local_ip, local_port, remote_ip, remote_port):
        f = open(filename, 'r')  #
        userid = None
        for line in f:
            m = Netstat._proc_net_tcp_re.match(line)
            if not m:
                continue
            if m.group(Netstat.IDX_LOCAL_IP) != local_ip:
                continue
            if m.group(Netstat.IDX_LOCAL_PORT) != local_port:
                continue
            if m.group(Netstat.IDX_REMOTE_IP) != remote_ip:
                continue
            if m.group(Netstat.IDX_REMOTE_PORT) != remote_port:
                continue
            userid = int(m.group(Netstat.IDX_USERID))
            break
        f.close()
        return userid
    
    @staticmethod
    def get_socket_owner_ipv4(local_ip, local_port, remote_ip, remote_port):
        local_port = Netstat.port_to_hex(local_port)
        local_ip = Netstat.ipv4_to_hex(local_ip)
        remote_port = Netstat.port_to_hex(remote_port)
        remote_ip = Netstat.ipv4_to_hex(remote_ip)
        return Netstat.get_socket_owner_file('/proc/net/tcp', local_ip, local_port, remote_ip, remote_port)
    
    @staticmethod
    def get_socket_owner(local_ip, local_port, remote_ip, remote_port):
        # prepare adresses
        _locals = socket.getaddrinfo(local_ip, local_port, 0, 0, socket.SOL_TCP)
        # [(2, 1, 6, '', ('127.0.0.1', 4282))]
        _remotes = socket.getaddrinfo(remote_ip, remote_port, 0, 0, socket.SOL_TCP)
        # [(2, 1, 6, '', ('127.0.0.1', 53726))]
        
        for local in _locals:
            for remote in _remotes:
                if remote[0] != local[0]:
                    continue
                if remote[4][0] != local[4][0]:
                    continue
                if remote[0] == socket.AF_INET:
                    return Netstat.get_socket_owner_ipv4(local[4][0], local[4][1], remote[4][0], remote[4][1])
                if remote[0] == socket.AF_INET6:
                    return Netstat.get_socket_owner_ipv6(local[4][0], local[4][1], remote[4][0], remote[4][1])
        return None
        
# Base class definitin for Extensions
class AbstractExtension(object):

    def __init__(self, server):
        self.server = server
        
    def get_name(self):
        raise NotImplementedError

    def dependencies(self):
        raise NotImplementedError

    def setup(self, extensionList):
        raise NotImplementedError

    def css(self, file):
        self.server.controller.add_common_css(vispa.url.static(file, extension=self.get_name()))

    def js(self, file):
        self.server.controller.add_common_js(vispa.url.static(file, extension=self.get_name()))

    def controller(self, controller):
        self.server.controller.mount_extension_controller(self.get_name(), controller)
        
    def remote(self, folder="remote"):
        local = os.path.join(os.path.dirname(inspect.getabsfile(self.__class__)), folder)
        remote = os.path.join('vispa', 'extensions', self.get_name(), folder)
        vispa.rpc.add_directory_files(local, remote)
        
_extensions = {}

def loadExtensions(server):
    # loop through all extensions and import their files
    # so that 'AbstractExtension' will know about its subclasses
    modulenames = []
    ignored = config('extensions', 'ignore', [])
    vispa.extensions.__path__.append(vispa.datapath('extensions'))
    for _importer, modulename, ispkg in pkgutil.iter_modules(vispa.extensions.__path__):
        if not ispkg:
            continue
        if modulename in ignored:
            logger.info('Ignore extension: %s '% modulename)
            continue
        try:
            importlib.import_module('vispa.extensions.%s' % modulename)
            modulenames.append(modulename)
        except:
            _, message, _ = sys.exc_info()
            logger.warning('Exception importing extension %s: %s' % (modulename, message))
            log_exception()

    for _importer, modulename, ispkg in pkgutil.iter_modules():
        if not ispkg:
            continue
        if not modulename.startswith('vispa_'):
            logger.info('Not a vispa extension: %s '% modulename)
            continue
        if modulename in ignored:
            logger.info('Ignore extension: %s '% modulename)
            continue
        try:
            importlib.import_module(modulename)
            modulenames.append(modulename)
        except:
            _, message, _ = sys.exc_info()
            logger.warning('Exception importing extension %s: %s' % (modulename, message))
            log_exception()
            
    load = [x.strip() for x in config('extensions', 'import', '').split(',')]
    load = filter(lambda x: len(x) > 0, load)
    for ext in load:
        logger.info('Import extension: %s '% ext)
        try:
            importlib.import_module(ext)
            modulenames.append(ext.split('.')[-1])
        except:
            _, message, _ = sys.exc_info()
            logger.warning('Exception importing extension %s: %s' % (modulename, message))
            log_exception()

    # instantiate all subclasses of the 'AbstractExtension'
    dependencies = {}
    for cls in AbstractExtension.__subclasses__():
        # check: is the modulename accepted?
        modulename = cls.__module__.split('.')[-1]
        if modulename in ignored:
            continue

        logger.debug('Loading Extension "%s"' % cls)
        extension = cls(server)
        name = extension.get_name()
        if name in _extensions.keys():
            raise Exception("Fail to load extension: '%s'. It already exsits!" % name)
        _extensions[name] = extension
        # update the 'dependencies' dict
        for dep in extension.dependencies():
            if dep not in dependencies.keys():
                dependencies[dep] = [name]
            else:
                dependencies[dep].append(name)

    # check dependencies
    for dep in dependencies.keys():
        if dep not in _extensions:
            data = dep, str(dependencies[dep])
            raise Exception("The following dependency could not be found: '%s'. The following extensions depend on it: %s" % data)

    # setup all valid extenions
    for extension in _extensions.values():
        extension.setup(_extensions)

def getExtension(name):
    return _extensions[name]

def getExtensions():
    return _extensions.values()
