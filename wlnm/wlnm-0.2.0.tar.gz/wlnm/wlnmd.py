
'''

wlnmd.py
==========

Desc: run wlnm deamon as SimpleXMLRPCServer


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''


from SimpleXMLRPCServer import SimpleXMLRPCServer
from daemon import Daemon
from os.path import expanduser
import os


import remoter
import util

def list_contents(dir_name):
	return os.listdir(dir_name)

def searchAll():
	return remoter.searchAll()

def show(args):
	return remoter.show(args)

def showWLS():
	return remoter.showWLS()

def showDomains():
	return remoter.showDomains()

def nmstart(args):
	return remoter.nmstart(args)

def startAdmin(args):
	return remoter.startAdmin(args)

def startServers(args):
	return remoter.startServers(args)

def stopServers(args):
	return remoter.stopServers(args)

def listprocess():
	return remoter.listprocess()

def kill(args):
	return remoter.kill(args)

wlnmd_pid_file = "%s/.wlnm/wlnm.pid" % expanduser("~")

class wlnmDaemon(Daemon):
	
	
	def __init__(self,pidfile, port,stdin=os.devnull, stdout=os.devnull, stderr=os.devnull, home_dir='.', umask=022, verbose=1):
		wlnmd_out_file = "%s/.wlnm/wlnm.out" % expanduser("~")
		self.stdin = stdin
		self.stdout = wlnmd_out_file
		self.stderr = wlnmd_out_file
		self.pidfile = pidfile
		self.home_dir = home_dir
		self.verbose = verbose
		self.umask = umask
		self.daemon_alive = True
		self.port = port


        def run(self):
                server = SimpleXMLRPCServer(('0.0.0.0', self.port), logRequests=True)
		server.register_function(list_contents)
		server.register_function(searchAll)
		server.register_function(show)
		server.register_function(showWLS)
		server.register_function(showDomains)
		server.register_function(nmstart)
		server.register_function(startAdmin)
		server.register_function(startServers)
		server.register_function(stopServers)
		server.register_function(listprocess)
		server.register_function(kill)

		try:
			#print 'Use Control-C to exit'
			server.serve_forever()
		except KeyboardInterrupt:
			print 'Exiting'

	



def runDaemon(iport):
	
	daemon = wlnmDaemon(pidfile=wlnmd_pid_file,port=iport)
	daemon.start()
	print "wlnm daemon "


def stopDaemon():
	
	if os.path.isfile(wlnmd_pid_file):
	    with open(wlnmd_pid_file) as f:
		pids = f.readlines()
	    try:
		os.kill(int(pids[0]),9)	#force kill
		print "wlnmd process %s is stopped ." % int(pids[0])
	    except :
		print "wlnmd process %s was killed before ." % int(pids[0])
	    finally :
		os.remove(wlnmd_pid_file)
	else :
	    print "wlnmd is not running , no process can be stopped."
	
	print

#runDaemon(9099)
#stopDaemon()
