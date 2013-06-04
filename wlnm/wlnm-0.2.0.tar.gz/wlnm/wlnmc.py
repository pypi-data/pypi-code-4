
'''

wlnmc.py
==========

Desc:  wlnm client as SimpleXMLRPC client


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import xmlrpclib
import util
import inputer

def connect(args):
	global host
	global port
	global proxy

	
	try:
		host= args[0]
		port= args[1]
		proxy = xmlrpclib.ServerProxy('http://%s:%s' % (host,port))
		proxy.list_contents('.')
		inputer.remote = True
	except:
		print 'not able to connect to http://%s ,make sure port and host is corrected' % ':'.join(args)
		inputer.remote = False

def searchAll():
	print util.decode_output(proxy.searchAll())

def show(args):
	print util.decode_output(proxy.show(args))

def showWLS():
	print util.decode_output(proxy.showWLS())

def showDomains():
	print util.decode_output(proxy.showDomains())

def nmstart(args):
	print util.decode_output(proxy.nmstart(args))

def startAdmin(args):
	print util.decode_output(proxy.startAdmin(args))

def startServers(args):
	print util.decode_output(proxy.startServers(args))

def stopServers(args):
	print util.decode_output(proxy.stopServers(args))

def listprocess():
	print util.decode_output(proxy.listprocess())

def kill(args):
	print util.decode_output(proxy.kill(args))

def disconnect():
	proxy = None
	host = None
	port = None
	inputer.remote = False


#connect(["localhost","9099"])
#print proxy.list_contents('/tmp')