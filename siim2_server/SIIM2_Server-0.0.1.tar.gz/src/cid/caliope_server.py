#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@authors: Andrés Felipe Calderón andres.calderon@correlibre.org
          Sebastián Ortiz V. neoecos@gmail.com

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Cid Server is the web server of SIIM2 Framework
Copyright (C) 2013 Infometrika Ltda.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
#system, and standard library
import os
import getopt
import sys
import importlib
from logging import getLogger

#gevent
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from gevent import monkey

#flask
from flask import Flask
from flask.helpers import safe_join

#Apps import
from modules.core.module_manager import module_loader
from utils.fileUtils import loadJSONFromFile, send_from_memory, Gzip

#: Gevent to patch all TCP/IP connections
monkey.patch_all()
app = Flask(__name__)


@app.route('/')
def index():
    return send_from_memory(safe_join(app.config['STATIC_PATH'], 'index.html'))
    #return render_template('index.html')


@app.route('/<path:filename>')
def custom_static(filename):
    return send_from_memory(safe_join(app.config['STATIC_PATH'], filename))


def main(argv):
    init_flask_app()
    config_file = _parseCommandArguments(argv)
    configure_server_and_app(config_file)
    configure_logger("conf/logger.json")
    register_modules()
    run_server()


def init_flask_app():
    app.secret_key = os.urandom(24)
    #: Disable internal debugger
    app.use_debbuger = False
    app.use_reloader = False
    #: load gzip compressor
    gzip = Gzip(app)


def _parseCommandArguments(argv):
    config_file = "conf/caliope_server.json"
    try:
        opts, args = getopt.getopt(argv, "hc:", ["help", "config="])
    except getopt.GetoptError:
        print 'caliope_server.py -c <configfile>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print 'caliope_server.py -c <configfile>'
            sys.exit()
        elif opt in ("-c", "--config"):
            config_file = arg
    return config_file


def configure_server_and_app(config_file):
    config = loadJSONFromFile(config_file, app.root_path)
    #TODO: Validate 'server' in config and load default if not present
    if 'address' in config['server']:
        app.config['address'] = config['server']['address']
    else:
        app.config['address'] = 'localhost'
    if 'port' in config['server']:
        app.config['port'] = int(config['server']['port'])
    else:
        app.config['port'] = 8000
    if 'static' in config['server']:
        app.config['STATIC_PATH'] = config['server']['static']
    else:
        app.config['STATIC_PATH'] = "."
    if 'formTemplates' in config['server']:
        app.config['FORM_TEMPLATES'] = config['server']['formTemplates']
    else:
        app.config['FORM_TEMPLATES'] = app.config['STATIC_PATH']
    #: Load app config
    if 'app' in config:
        if 'modules' in config['app']:
            app.config['modules'] = config['app']['modules']
        else:
            app.config['modules'] = {'dispatcher': {'module_name': 'src.cid.modules.core.dispatcher',
                                     'module_route': '/api'}}
    else:
        #TODO: Load all default app config
        pass
    if 'debug' in config['server']:
        app.debug = True if config['server']['debug'] == 'True' else False
    else:
        app.debug = False


def configure_logger(config_file):
    config = loadJSONFromFile(config_file, app.root_path)
    from logging.config import dictConfig
    dictConfig(config)


def register_modules():
    """
    Register modules listed in the configuration of the app.

    """
    for module in app.config['modules']:
        module_config = module.values()[0]
        module_name = module_config['module_name'] if 'module_name' in module_config else ''

        #: default route is /module_name
        module_route = module_config['module_route'] if 'module_route' in module_config else '/' \
                      + module_config['module_name']
        #:TODO  Is possible to only module to have more than 1 blueprint
        blueprint_name = module_config['module_blueprint'] if 'module_blueprint' in module_config else \
                      module_config['module_name'].split('.')[-1]
        try:
            module_blueprint = importlib.import_module('cid.modules.' + module_name)
            app.register_blueprint(module_blueprint.getBlueprint(), url_prefix=module_route)
        except Exception:
            app.logger.exception(str(Exception))


def run_server():
    if not app.debug:
        Flask.logger = getLogger("production")
    else:
        Flask.logger = getLogger("develop")
    app.logger.info("Starting server on: " + app.config['address'] + ":" + str(app.config['port']))
    app.logger.info("Static Base Directory: " + app.config['STATIC_PATH'])
    app.logger.info("Forms Template Directory : " + app.config['FORM_TEMPLATES'])
    http_server = WSGIServer((app.config['address'], app.config['port']), app,
                             handler_class=WebSocketHandler)  # @IgnorePep8
    http_server.serve_forever()


if __name__ == '__main__':
    #: Start the application
    main(sys.argv[1:])
