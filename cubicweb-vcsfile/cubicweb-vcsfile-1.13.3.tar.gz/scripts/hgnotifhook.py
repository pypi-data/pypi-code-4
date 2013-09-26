#!/usr/bin/python
# -*- coding: utf-8 -*-

# A simple Mercurial hook to send update notifications to a
# cubicweb-vcsfile instance (via a broker, see notifbroker.py). As is,
# it makes the assumption that repos are organized under a 'root'
# directory called 'repos'. This is well suited for a
# Mercurial-server¹ based configuration.
#
# ¹: http://www.lshift.net/mercurial-server.html

import zmq
import os
import time

context = zmq.Context()
req_sock = context.socket(zmq.PUSH)
req_url = os.environ.get('HG_NOTIF_URL', 'tcp://127.0.0.1:5556')
req_sock.connect(req_url)

cwd = os.environ['PWD']
msg = cwd.split('/repos/')[-1].rstrip('/')
req_sock.send(msg)

# make sure the socket has some time to send the payload
time.sleep(0.5)
# make sure we won't block on exit event is there is no listening server
req_sock.close(linger=0)

print 'Sent ZMQ notification for', msg, 'to', req_url
