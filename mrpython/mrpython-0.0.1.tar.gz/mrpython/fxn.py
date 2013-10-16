# -*- coding: utf-8 -*-

import logging
import inspect
import socket
import struct

def autolog(message=None, level=logging.DEBUG):
	func = inspect.currentframe().f_back.f_code
	frame = inspect.stack()[1]
	values = inspect.formatargvalues(*inspect.getargvalues(frame[0]))
	module = inspect.getmodule(frame[0])
	logger = logging.getLogger(module.__name__)
	logger.log(level, '%s [%s] : %s' % (func.co_name, values, message))

def enum(**enums):
	return type('Enum', (), dict(enums.items() + {'items': enums}.items()))

def ip2long(ip):
	packed = socket.inet_aton(ip)
	return long(struct.unpack('!L', packed)[0])

def long2ip(lg):
	return socket.inet_ntoa(struct.pack('!L', lg))