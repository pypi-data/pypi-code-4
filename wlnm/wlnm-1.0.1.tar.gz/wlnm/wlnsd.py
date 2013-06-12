
'''

wlnsd.py
==========

Desc: run wlnm server deamon as SimpleXMLRPCServer


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''


from SimpleXMLRPCServer import SimpleXMLRPCServer

from os.path import expanduser
import os
import sys

import server
import util
from daemon import Daemon
import database

def list_contents(dir_name):
	return os.listdir(dir_name)

def initMachine(machine, port):
	return server.initMachine(machine, port)

def showMachines():
	return server.showMachines()

def useMachine(args):
	return server.useMachine(args)

def show(args):
	return server.show(args)

def showWLS(machine):
	return server.showWLS(machine)

def showDomains(machine):
	return server.showDomains(machine)

def nmstart(args):
	return server.nmstart(args)

def startAdmin(args):
	return server.startAdmin(args)

def startServer(args):
	return server.startServer(args)

def stopServer(args):
	return server.stopServer(args)

def listprocess(machine):
	return server.listprocess(machine)

def kill(args):
	return server.kill(args)

wlnsd_pid_file = "%s/.wlnm/wlnsd.pid" % expanduser("~")

database.creatProfileDir()

class ServerDaemon(Daemon):
	
	
	def __init__(self,pidfile, port,stdin=os.devnull, stdout=os.devnull, stderr=os.devnull, home_dir='.', umask=022, verbose=1):
		wlnsd_out_file = "%s/.wlnm/wlnsd.out" % expanduser("~")
		self.stdin = stdin
		self.stdout = wlnsd_out_file
		self.stderr = wlnsd_out_file
		self.pidfile = pidfile
		self.home_dir = home_dir
		self.verbose = verbose
		self.umask = umask
		self.daemon_alive = True
		self.port = port

	def start(self):

		# Check port see if it is open
		if util.checkport(self.port) :
			message = "port %s is occupied by other process\n"
                        sys.stderr.write(message % self.port)
                        sys.exit(1)
		super(ServerDaemon, self).start()

        def run(self):
		database.checkdb()
                server = SimpleXMLRPCServer(('0.0.0.0', self.port), logRequests=True)
		server.register_function(list_contents)
		server.register_function(initMachine)
		server.register_function(useMachine)
		server.register_function(showMachines)
		server.register_function(show)
		server.register_function(showWLS)
		server.register_function(showDomains)
		server.register_function(nmstart)
		server.register_function(startAdmin)
		server.register_function(startServer)
		server.register_function(stopServer)
		server.register_function(listprocess)
		server.register_function(kill)
		print "wlnm server daemon is running ."
		try:
			#print 'Use Control-C to exit'
			server.serve_forever()
		except KeyboardInterrupt:
			print 'Exiting'

	



def runDaemon(iport):
	print "Start wlnm server daemon ."
	daemon = ServerDaemon(pidfile=wlnsd_pid_file,port=iport)
	daemon.start()
	


def stopDaemon():
	
	if os.path.isfile(wlnsd_pid_file):
	    with open(wlnsd_pid_file) as f:
		pids = f.readlines()
	    try:
		os.kill(int(pids[0]),9)	#force kill
		print "wlnm server process %s is stopped ." % int(pids[0])
	    except :
		print "wlnm server process %s was killed before ." % int(pids[0])
	    finally :
		os.remove(wlnsd_pid_file)
	else :
	    print "wlnm server is not running , no process can be stopped."
	
	print

#runDaemon(9099)
#stopDaemon()
