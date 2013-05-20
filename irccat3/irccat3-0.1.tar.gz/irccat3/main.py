from __future__ import absolute_import

import argparse
import logging
import multiprocessing
import Queue
import signal
import sys

from irccat3 import bot, listener

log = logging.getLogger(__name__)


def get_args(argv):
    parser = argparse.ArgumentParser()

    parser.add_argument("--verbose", help="increase output verbosity")

    parser.add_argument("--irc-server", help="IRC server to connect to.",
                        default='localhost')
    parser.add_argument("--irc-port", help="Port for irc server",
                        type=int, default=6667)
    parser.add_argument("--irc-channel", help="IRC channel to publish to",
                        default='#irccat')

    parser.add_argument("--listen-interface", 
                        help="network interface to listen on.  Defaults to all of them.",
                        default='0.0.0.0')
    parser.add_argument("--listen-port", 
                        help="Port to listen on (default 12345)",
                        type=int, default=12345)

    args = parser.parse_args(argv)

    return args

def main():
    args = get_args(sys.argv[1:])

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    log.info('args: %r', args)

    q = Queue.Queue()

    l = listener.TCPServer(q, args.listen_interface, args.listen_port)

    c = bot.IRCCat(args.irc_channel, q, l)
    c.connect(args.irc_server, args.irc_port, "catbot")
    c.start()


