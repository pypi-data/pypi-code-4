#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 Etienne Robillard  <erob@gthcfoundation.org>
# All rights reserved
# <LICENSE=ISC>
"""Another stand-alone HTTP server for serving Django apps in pure
WSGI context with the ``wsgiref`` module. 
"""

import os,sys,logging,warnings

try:
    import argparse2 as argparse
except ImportError:
    import argparse

from notmm.utils.http import HTTPServer, get_bind_addr, daemonize
from notmm.utils.configparse import loadconf
from notmm.utils.pastecompat import eval_import
from notmm.utils.django_settings import SettingsProxy

log = logging.getLogger('notmm.controllers.wsgi')

# quick and dirty logging dispatcher
_ = lambda x: log.debug(x)

__all__ = ['auth_module', 'parse_cmdline', 'exit', 'main']

# Defaults configuration values
_defaults = {
    'DEBUG'             : os.environ.get('DJANGO_DEBUG', bool(__debug__ == True)),
    'auth_module'       : 'authkit',
    'WSGIHandlerClass'  : eval_import('notmm.controllers.wsgi:WSGIController'),
    'WSGIRequestClass'  : eval_import('notmm.utils.wsgilib.request:HTTPRequest')
    }


def parse_cmdline(argv):
    parser = argparse.ArgumentParser(__file__)
    parser.add_argument('-d', '--debug', action="store_true", \
        help="Enable Debugging mode", default=False)
    parser.add_argument('-c', '--config', dest="filename",
        default="development.ini", nargs=1, \
        help="Path to a development.ini-like file")
    parser.add_argument('-s', '--ssl', action="store_true", \
        dest="enable_ssl", \
        help="Enable SSL transport mode (not implemented!)")
    parser.add_argument('--disable-authkit', action="store_true", \
        dest="disable_authkit", \
        help="Disable session middleware backend (authkit)", default=True)
    parser.add_argument('--disable-xdserver', action="store_true", \
        dest="disable_xdserver", \
        help="Disable xdserver network database backend", default=False)
    parser.add_argument('--settings', dest="disable_settings", nargs=1, \
        required=False, help="TARGET settings module", default=False)
    # add support for custom PYTHONPATH 
    parser.add_argument('--pythonpath', dest="pythonpath", default=None, \
        required=False)
    
    # show version with --version
    parser.add_argument('--version', dest="version", \
        help="Show the current version")

    # app_label hint
    parser.add_argument('app_label', type=str, \
        help="TARGET application to launch")
    
    options = parser.parse_args(args=argv[1:])
    return options

def exit(retcode):
    sys.exit(retcode)

def main(argv):
    # Start the http server after having parsed
    # options defined in the development.ini file. 

    # Read the default configuration file
    options = parse_cmdline(sys.argv)

    #if options.debug is not False: settings.DEBUG = True # override 

    if options.pythonpath is not None:
        for path in options.pythonpath.split(':'):
            #if DEBUG:
            #    print 'Path: %r' % path 
            sys.path.insert(0, path)

    if options.filename:
        global_conf = loadconf(options.filename[0])
        if 'defaults' in global_conf:
            _defaults.update(global_conf['defaults'])
    else:
        warnings.warn('Please specify a valid config file path')

    #print global_conf
    app_conf = global_conf[options.app_label]

    #FIXME
    try:
        WSGIRequestClass = eval_import(app_conf['wsgi.request_class'])
    except NameError:
        WSGIRequestClass = _defaults['WSGIRequestClass']

    # A INET4 address to bind to for listening for HTTP connections -> (host, port)
    bind_addr = get_bind_addr(global_conf)
    
    # Use command line settings module if set
    if not options.disable_settings:
        settings_module = os.environ['DJANGO_SETTINGS_MODULE']

    else:
        settings_module = options.disable_settings[0]
    
    settings = SettingsProxy(settings_module, autoload=True).get_settings() # Load them all
    
    if not 'controller' in app_conf:
        # Default app. To change this behavior, specify an alternative
        # "controller" param in the config file (development.ini)
        WSGIHandlerClass = _defaults['WSGIHandlerClass']
    else:
        WSGIHandlerClass = eval_import(app_conf['controller'])
    
    if settings.DEBUG: 
        _('WSGIController class=%s' % str(WSGIHandlerClass.__name__))
        _("%d settings found in settings module: %r" % (settings.count(), settings_module))
    
    # Initialize the app with user-defined settings
    # default to 'authkit' unless --disable-authkit param
    # is given
    if not options.disable_authkit and 'authkit' in global_conf:
        auth_conf = global_conf['authkit'] # authkit config
    else:
        auth_conf = None
    
    # This is the generic interface to the WSGIController extension
    wsgi_app = WSGIHandlerClass(
        None, # stand-alone mode 
        settings=settings,
        app_conf={'django.settings_autoload': True,
                  'logging.disabled': False}
        )
    #import pdb; pdb.set_trace()

    
    # Install the caching/session middleware (Beaker)
    if settings.ENABLE_BEAKER:
        if 'beaker' in global_conf:
            session_conf = global_conf['beaker']
            print session_conf
        from beaker.middleware import SessionMiddleware
        #Install the SessionMiddleware
        wsgi_app = SessionMiddleware(wsgi_app)
        _("Experimental Beaker backend initialized: %r" % wsgi_app)
    else:
        _("Beaker is disabled by config. Set ENABLE_BEAKER=True to enable memcached support.")

    # Enable the authentication middleware (LoginController)
    # unless the "disable_authkit" option has been set
    if options.disable_authkit is not True and _defaults['auth_module'] in global_conf:
        auth_module = _defaults['auth_module']
        from notmm.controllers.auth import AuthCookieController
        #auth_conf = global_conf[auth_module]
        #auth_conf['handle_exceptions'] = False
        wsgi_app = AuthCookieController(wsgi_app, auth_conf=auth_conf, settings=settings)
    else:
        _("Authentication middleware disabled.")

    daemonize(wsgi_app, bind_addr)

if __name__ == "__main__":
   #assert len(sys.argv) >= 2, 'usage: runserver.py host:port' 
   main(argv=sys.argv)

