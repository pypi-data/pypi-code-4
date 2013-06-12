
'''

wlnad.py
==========

Desc: run wlnm agent deamon as SimpleXMLRPCServer


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''


from SimpleXMLRPCServer import SimpleXMLRPCServer
from daemon import Daemon
from os.path import expanduser
import os
import sys


import agent
import util
import database

def list_contents(dir_name):
	return os.listdir(dir_name)

def searchAll():
	return agent.searchAll()

def nmstart(wls_home):
	return agent.nmstart(wls_home)

def startAdmin(domainhome):
	return agent.startAdmin(domainhome)

def startServer(args):
	return agent.startServer(args)

def stopServer(args):
	return agent.stopServer(args)

def listprocess():
	return agent.listprocess()

def kill(args):
	return agent.kill(args)

wlnad_pid_file = "%s/.wlnm/wlnad.pid" % expanduser("~")

database.creatProfileDir()

class AgentDaemon(Daemon):
	
	
	def __init__(self,pidfile, port,stdin=os.devnull, stdout=os.devnull, stderr=os.devnull, home_dir='.', umask=022, verbose=1):
		wlnad_out_file = "%s/.wlnm/wlnad.out" % expanduser("~")
		self.stdin = stdin
		self.stdout = wlnad_out_file
		self.stderr = wlnad_out_file
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
		super(AgentDaemon, self).start()
	
	def run(self):
                server = SimpleXMLRPCServer(('0.0.0.0', self.port), logRequests=True)
		server.register_function(list_contents)
		server.register_function(searchAll)
		server.register_function(nmstart)
		server.register_function(startAdmin)
		server.register_function(startServer)
		server.register_function(stopServer)
		server.register_function(listprocess)
		server.register_function(kill)
		

		try:
			#print 'Use Control-C to exit'
			server.serve_forever()
		except KeyboardInterrupt:
			print 'Exiting'

	



def runDaemon(iport):
	print "Start wlnm agent daemon ."
	daemon = AgentDaemon(pidfile=wlnad_pid_file,port=iport)
	daemon.start()
	


def stopDaemon():
	
	if os.path.isfile(wlnad_pid_file):
	    with open(wlnad_pid_file) as f:
		pids = f.readlines()
	    try:
		os.kill(int(pids[0]),9)	#force kill
		print "wlnm agent process %s is stopped ." % int(pids[0])
	    except :
		print "wlnm agent process %s was killed before ." % int(pids[0])
	    finally :
		os.remove(wlnad_pid_file)
	else :
	    print "wlnm agent is not running , no process can be stopped."
	
	print

#runDaemon(9099)
#stopDaemon()
