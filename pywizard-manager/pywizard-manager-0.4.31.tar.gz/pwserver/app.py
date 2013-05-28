import argparse
import json
import logging
import django.core.handlers.wsgi
import os
import sys
from django.core.management import execute_from_command_line
from pwmanager.settings import DATABASES, PROVISION_PACKAGE_UPLOAD_DIRECTORY
from pywizard.utils.config import read_yaml_cofig
from pywizard.utils.process import require_sudo, run
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
from pwmanager import settings

from pwmanager.wsgi import application
from pwmanager.pwconfig import PwManagerConfigSource

from zmq.eventloop import ioloop
from pwserver.server import WebSocketHandler, PywizardServer

ioloop.install()


class NodeCfgHandler(tornado.web.RequestHandler):
    config_source = None

    def initialize(self, config_source=None):
        super(NodeCfgHandler, self).initialize()
        self.config_source = config_source

    def get(self, node_name):
        self.write(json.dumps(self.config_source.get_node_config(node_name), indent=True, sort_keys=True))


def update_settings(config):
    settings.DATABASES['default']['NAME'] = config['db_file']
    settings.PROVISION_PACKAGE_UPLOAD_DIRECTORY = config['upload_dir']


def prepare_directories(config):
    if not os.path.exists(config['upload_dir']):
        os.makedirs(config['upload_dir'], 0700)

    if not os.path.exists('/var/pywizard/static'):
        os.makedirs('/var/pywizard/static', 0700)


def prepare_db(config):
    db_file = config['db_file']
    if not os.path.exists(os.path.dirname(db_file)):
        os.makedirs(os.path.dirname(db_file), 0700)
    if not os.path.exists(db_file):
        execute_from_command_line(['manage.py', 'syncdb', '--noinput'])
        os.chmod(db_file, 0700)


def collect_static_resources():
    args = ['manage.py', 'collectstatic', '--noinput']
    if os.name == 'posix':
        args.append('-l')
    execute_from_command_line(args)


def run_django(config):
    update_settings(config)
    prepare_directories(config)

    wsgi_app = tornado.wsgi.WSGIContainer(application)

    print config

    prepare_db(config)
    collect_static_resources()

    return wsgi_app


def run_server(config):
    wsgi_app = run_django(config)

    config_source = PwManagerConfigSource()

    pwserver = PywizardServer(config_source)
    pwserver.bind_sockets(config['sockets']['host'])

    tornado_app = tornado.web.Application(
        [
            # 3(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": cur_path + '/static/'}),
            (r"/io", WebSocketHandler, {'pywizard_server': pwserver}),
            (r"/node-cfg/(.*)", NodeCfgHandler, {'config_source': config_source}),
            ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
        ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(config['web']['port'])

    logging.info('Web-server started at port %d' % config['web']['port'])

    ioloop.IOLoop.instance().start()


def run_server_cmd():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, nargs='?')
    parser.set_defaults(config=None)
    parser.add_argument('--install', action='store_true', default=False)
    parser.add_argument('--add-user', action='store_true', default=False)
    args = parser.parse_args()

    if args.install:
        require_sudo()

        path = os.path.dirname(__file__) + '/templates/upstart-server.conf'
        run('cp %s /etc/init/pywizard-server.conf' % path)
        run('chmod +x /etc/init/pywizard-server.conf')
        run('start pywizard-server')
        run('status pywizard-server')

    else:

        logging.basicConfig(level=logging.INFO)

        config_file = None
        if not args.config:
            curdir_server_yml_ = os.path.curdir + '/server.yml'
            etc_pywizard_server_yml = '/etc/pywizard/server.yml'

            if os.path.exists(curdir_server_yml_):
                config_file = curdir_server_yml_
            elif os.path.exists(etc_pywizard_server_yml):
                config_file = etc_pywizard_server_yml
            else:
                sys.stderr.write("\n\n\nConfig file was not found in current directory (%s) or /etc (%s). "
                                 "You can specify it manualy with parameter '--config'" % (
                                     curdir_server_yml_,
                                     etc_pywizard_server_yml
                                 ))
                exit(1)
        else:
            config_file = args.config

        config = read_yaml_cofig(config_file)

        if args.add_user:
            run_django(config)
            execute_from_command_line(['manage.py', 'createsuperuser'])
        else:
            run_server(config)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    run_server_cmd()