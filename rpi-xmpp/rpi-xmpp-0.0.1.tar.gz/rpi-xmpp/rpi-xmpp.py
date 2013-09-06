#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
import logging
import os
import threading
import argparse

import sleekxmpp
import RPIO

import sys
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding("utf8")

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
slog = logging.getLogger(__name__)

rc = {}

def read_config():
    rcfile = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    rcfile = os.path.join(os.environ['HOME'], ".%s" % rcfile)
    parser = argparse.ArgumentParser(description = "Send XMPP notifications of GPIO events",
                                     formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--config", default = rcfile, help = "config file to use")
    parser.add_argument("--jid", help = "sender JID")
    parser.add_argument("--password", help = "password for sender JID")
    parser.add_argument("--gpio", type = int, default = 14, help = "GPIO to watch")
    parser.add_argument("-r", "--recipient", help = "send message to this recipient")
    parser.add_argument("-m", "--message", default = "GPIO event", help = "message to send")

    args = parser.parse_args()

    if args.config:
        rcfile = args.config
    if os.access(rcfile, os.R_OK):
        for ln in open(rcfile).readlines():
            key, val = ln.strip().split('=', 1)
            rc[key.lower()] = val

    opts = ["jid", "password", "gpio", "recipient", "message"]
    for opt in opts:
        if getattr(args, opt):
            rc[opt] = getattr(args, opt)
    rc["gpio"] = int(rc["gpio"])

class Msg(sleekxmpp.ClientXMPP):
    def __init__(self, rcpt, msg):
        super(Msg, self).__init__(rc["jid"], rc["password"])
        self.add_event_handler("session_start", self.session_start)

        self.rcpt = rcpt
        self.msg = msg

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        self.send_message(self.rcpt, self.msg)
        self.disconnect(wait=True)

def gpio_callback(gpio_id, val):
    msg = Msg(rc["recipient"], rc["message"])
    if not msg.connect():
        slog.error("unable to send message")
        return
    msg.process(block=True)
    slog.info("message sent")

def handle_gpio():
    RPIO.add_interrupt_callback(int(rc["gpio"]), gpio_callback, pull_up_down=RPIO.PUD_UP, edge="rising", debounce_timeout_ms=500, threaded_callback=True)
    slog.info("ready at gpio #%s" % rc["gpio"])
    RPIO.wait_for_interrupts()

if __name__ == "__main__":
    read_config()
    handle_gpio()
