# -*- coding: utf-8 -*-

import os
import cherrypy
import vispa
import vispa.url
import vispa.extensions
import vispa.tools.db
import vispa.tools.device
import vispa.tools.profile
import vispa.tools.stats
import vispa.tools.template
import vispa.tools.user
import vispa.tools.workspace
import vispa.tools.parameters
import vispa.plugins.db
import vispa.plugins.template
import logging
from logging import config as loggingcfg
import sqlalchemy

systemlog = logging.getLogger(__name__)

class Server(object):

    __default_server_config = {
        'tools.proxy.on': False,
        'server.socket_host': '127.0.0.1',
        'server.socket_port': 4282,
        'server.thread_pool': 10,
        'engine.autoreload_on': False
    }

    def __default_mount_config(self):
        return {
            '/': {
                'tools.sessions.on': True,
                'tools.encode.on': False,
                'tools.db.on': True,
                'tools.private_parameters.on': True,
                'tools.user.on': True,
                'tools.workspace.on': True,
                'tools.sessions.storage_type': 'file',
                'tools.sessions.storage_path': vispa.datapath('sessions'),
                'tools.sessions.timeout': 1440,
                'tools.staticdir.root': vispa.codepath('vispa', 'static'),
                'tools.gzip.on': True,
                'tools.gzip.mime_types': ['text/html', 'text/css', 'application/x-javascript', 'application/json'],
            },
            '/static': {
                'tools.db.on': False,
                'tools.user.on': False,
                'tools.workspace.on': False,
                'tools.etags.on': True,
                'tools.staticdir.on': True,
                'tools.staticdir.dir': '',
                'tools.sessions.on': False,
                'tools.expires.on': True,
                'tools.expires.secs': 3600*24*365,
            },
        }

    def __init__(self, args):
        self.__init_paths(args)
        self.__init_logging(args)
        self.__init_tools(args)
        self.__init_platform(args)
        self.__init_plugins(args)

    def __init_paths(self, args):
        # dir for variable files and folders
        self.var_dir = os.path.abspath(args.vardir)
        if not os.path.exists(self.var_dir):
            os.makedirs(self.var_dir)

        cherrypy.log('Using %s as data dir.' % self.var_dir, 'SERVER')
        vispa.set_datapath(self.var_dir)

        # log dir
        self.log_dir = os.path.join(self.var_dir, 'logs')
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)

        # session dir
        self.session_dir = os.path.join(self.var_dir, 'sessions')
        if not os.path.exists(self.session_dir):
            os.mkdir(self.session_dir)

        # dir for rpc files
        self.rpc_dir = os.path.join(self.var_dir, 'rpc')
        if not os.path.exists(self.rpc_dir):
            os.mkdir(self.rpc_dir)

        # cache dir
        self.cache_dir = os.path.join(self.var_dir, 'cache')
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        # conf dir
        self.conf_dir = os.path.abspath(args.configdir)
        cherrypy.log('Using %s as config dir.' % self.conf_dir, 'SERVER')
        vispa.set_configpath(self.conf_dir)
        vispa.config.read(vispa.configpath('vispa.ini'))
        

    def __init_logging(self, args):
        # setup the logging
        logging_conf = os.path.join(self.conf_dir, 'logging.ini')
        if os.path.isfile(logging_conf):
            loggingcfg.fileConfig(logging_conf)
        elif args.loglevel == "info":
            logging.basicConfig(level=logging.INFO)
            cherrypy.log.screen = False
            cherrypy.log.access_file = os.path.join(self.log_dir, "access.log")
        elif args.loglevel == "debug":
            logging.basicConfig(level=logging.DEBUG)
            cherrypy.log.screen = False
            cherrypy.log.access_file = os.path.join(self.log_dir, "access.log")
        else:
            cherrypy.log('Using default logging.', 'SERVER')
            cherrypy.log.access_file = os.path.join(self.log_dir, "access.log")
            cherrypy.log.screen = False

        # update the global settings for the HTTP server and engine
    def __init_tools(self, args):
        cherrypy.tools.render = vispa.tools.template.MakoTool({'base_dynamic': vispa.url.dynamic('/'), 'base_static': vispa.url.static('/', timestamp=False)})
        cherrypy.tools.db = vispa.tools.db.SATool()
        cherrypy.tools.user = vispa.tools.user.UserTool(vispa.url.dynamic('/login'))
        cherrypy.tools.workspace = vispa.tools.workspace.WorkspaceTool(vispa.url.dynamic('/workspace'))
        cherrypy.tools.private_parameters = vispa.tools.parameters.PrivateParameterFilter()
        cherrypy.tools.device = vispa.tools.device.DeviceTool()
        cherrypy.tools.profile = vispa.tools.profile.ProfileTool()
        cherrypy.tools.stats = vispa.tools.stats.StatsTool()
        if vispa.config('websockets', 'enabled', False):
            from vispa.tools.socket import WSTool
            cherrypy.tools.websocket = WSTool()

    def __init_plugins(self, args):
        if vispa.config('websockets', 'enabled', False):
            cherrypy.tools.websocket.set_platform(self.__platform)
            from ws4py.server.cherrypyserver import WebSocketPlugin
            WebSocketPlugin(cherrypy.engine).subscribe()

        vispa.plugins.template.MakoPlugin(cherrypy.engine, base_dir=os.path.dirname(__file__), module_dir=self.cache_dir).subscribe()
        self.sa_identifier = vispa.config('database', 'sqlalchemy.url', 'sqlite:///%s/vispa.db' % self.var_dir)
        cherrypy.log('Use database %s.' % self.sa_identifier, 'SERVER')
        self.sa_engine = sqlalchemy.create_engine(self.sa_identifier)
        vispa.plugins.db.SAPlugin(cherrypy.engine, self.sa_identifier).subscribe()

    def __init_platform(self, args):
        cherrypy.config.update(self.__default_server_config)
        
        cherrypy_conf = vispa.configpath('cherrypy.ini')
        if os.path.isfile(cherrypy_conf):
            cherrypy.config.update(cherrypy_conf)

        from vispa.controller.platform import PlatformController
        self.controller = vispa.controller.platform.PlatformController()
        vispa.loadExtensions(self)
        script_name = vispa.url.dynamic('/', encoding='utf-8')
        app = cherrypy.tree.mount(self.controller, script_name, self.__default_mount_config())
        if os.path.isfile(cherrypy_conf):
            app.merge(cherrypy_conf)

    def run(self):
        if hasattr(cherrypy.engine, 'signal_handler'):
            cherrypy.engine.signal_handler.subscribe()
        cherrypy.engine.start()
        cherrypy.engine.block()