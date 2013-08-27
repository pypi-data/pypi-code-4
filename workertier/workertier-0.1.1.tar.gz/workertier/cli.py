#coding:utf-8
import argparse
import logging

from gevent import pywsgi, monkey; monkey.patch_all()
from gevent.event import Event

from workertier.config import ConfigLoader
from workertier.handler import Handler
from workertier.consumer import Consumer


DEFAULT_WEB_HOST = "0.0.0.0"
DEFAULT_WEB_PORT = 8443
DEFAULT_CONFIG_PATH = "config.ini"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def start_web(cache, dispatcher, config):
    host = config.safe_get("web", "host", DEFAULT_WEB_HOST)
    port = config.safe_get("web", "port", DEFAULT_WEB_PORT)

    handler = Handler(cache, dispatcher)
    server = pywsgi.WSGIServer((host, port), handler.handle_request)
    server.start()

def start_consumer(cache, dispatcher, config):
    consumer = Consumer(cache, dispatcher)
    consumer.start()

def main(role, config_path):
    config = ConfigLoader(config_path)
    if not config.read_paths:
        logger.critical("No configuration file could be read at %s", config_path)
        logger.critical("Use the -c option to specify a valid configuration file")
        return

    cache = config.cache()
    dispatcher = config.dispatcher()
    ROLES[role](cache, dispatcher, config)

    # Just wait until the end of time now.
    event = Event()
    event.wait()


ROLES = {
    "web": start_web,
    "consumer": start_consumer
}


def cli():
    parser = argparse.ArgumentParser("workertier")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG_PATH, help="Path to a configuration file. "
                                                                            "Defaults to" + DEFAULT_CONFIG_PATH)
    parser.add_argument("role", help="The role we should run", choices=ROLES.keys())
    args = parser.parse_args()

    main(args.role, args.config)


if __name__ == "__main__":
    cli()
