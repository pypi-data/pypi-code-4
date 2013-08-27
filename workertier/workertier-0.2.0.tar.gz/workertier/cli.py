#coding:utf-8
import argparse
import logging

from daemon import DaemonContext
from lockfile.pidlockfile import PIDLockFile

from workertier.version import __version__
from workertier.config import ConfigLoader


LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

DEFAULT_CONFIG_PATH = "config.ini"
DEFAULT_PIDFILE_PATTERN = "/var/run/workertier.{role}.pid"  # Can be altered in proc.pidfile
DEFAULT_LOGFILE_PATTERN = "/var/log/workertier.{role}.log"  # Can be altered in proc.logfile
DEFAULT_UID = 0  # Can be altered in proc.uid
DEFAULT_GID = 0  # Can be altered in proc.gid
DEFAULT_LOGLEVEL = logging.DEBUG  # Can be altered in proc.log
DEFAULT_WEB_HOST = "0.0.0.0"  # Can be altered in web.host
DEFAULT_WEB_PORT = 8443       # Can be altered in web.port


def start_web(cache, dispatcher, config):
    # Lazy import since we might have to fork and would rather not mess up gevent.
    from gevent import pywsgi, monkey; monkey.patch_all()
    from workertier.handler import Handler

    host = config.safe_get("web", "host", DEFAULT_WEB_HOST)
    port = config.safe_get("web", "port", DEFAULT_WEB_PORT)

    handler = Handler(cache, dispatcher)
    server = pywsgi.WSGIServer((host, port), handler.handle_request)
    server.start()

def start_consumer(cache, dispatcher, config):
    from gevent import monkey; monkey.patch_all()
    from workertier.consumer import Consumer

    consumer = Consumer(cache, dispatcher)
    consumer.start()

def main(role, config):
    from gevent.event import Event

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
    parser.add_argument("-d", "--daemon", default=False, action="store_true", help="Daemonize this process")
    parser.add_argument("role", help="The role we should run", choices=ROLES.keys())
    args = parser.parse_args()

    config = ConfigLoader(args.config)
    if not config.read_paths:
        print "ERROR: No configuration file could be read at %s" % args.config
        print "       Use the -c option to specify a valid configuration file"
        return

    loglevel = config.safe_get("proc", "log", DEFAULT_LOGLEVEL)
    formatter = logging.Formatter(LOG_FORMAT)
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(loglevel)
    root_logger.addHandler(stderr_handler)

    if args.daemon:
        pidfile = config.safe_get("proc", "pidfile", DEFAULT_PIDFILE_PATTERN)
        logfile = config.safe_get("proc", "logfile", DEFAULT_LOGFILE_PATTERN)
        uid = config.safe_get("proc", "uid", DEFAULT_UID)
        gid = config.safe_get("proc", "gid", DEFAULT_GID)

        pidfile = pidfile.format(role=args.role)
        logfile = logfile.format(role=args.role)

        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

        root_logger.info("workertier v{0}: starting".format(__version__))

        with DaemonContext(pidfile=PIDLockFile(pidfile), files_preserve=[file_handler.stream], uid=uid, gid=gid):
            # noinspection PyBroadException
            try:
                main(args.role, config)
            except Exception:
                root_logger.exception("An fatal exception occurred")

    main(args.role, config)


if __name__ == "__main__":
    cli()
