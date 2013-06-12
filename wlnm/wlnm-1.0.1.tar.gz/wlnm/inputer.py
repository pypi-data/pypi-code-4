'''

inputer.py
==========

Desc: Helper module for command which user typed


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import sys
import readline


import util

from wlnsc import ServerClient


#server_inst = ServerClient(host="localhost",port="9099")
#server_inst.connect()

class remoteCmds():
	def __init__(self,server):
		self.server = server


		self.cmddict={'init':self.server.initMachine,
			'ls':self.server.show,
			'lswls':self.server.showWLS,
			'lsd':self.server.showDomains,
			'lsm':self.server.showMachines,
			'nmstart':self.server.nmstart,
			'help':util.help,
			'startadmin':self.server.startAdmin,
			'start':self.server.startServer,
			'stop':self.server.stopServer,
			'lsp':self.server.listprocess,
			'kill':self.server.kill,
			'use':self.server.setMachine,
			'disconnect':self.server.disconnect,
			'quit':sys.exit
		}

		self.cmds=self.cmddict.keys()

	def runcmd(self,command,args):
	
		if command not in self.cmds:
			print 'Invilad command! Press Tab key or use help command list all avaiable command.'
			print ''
		else:
			if not args :
				if command == "ls" :
					self.cmddict[command]([])
				else :
					self.cmddict[command]()
			else:
				self.cmddict[command](args)



	def validcmd(self,command,args):
		#print self.server.machine
		#print command
		if command in ["ls","lsd" ,"lsp" ,"lswls" ,"disconnect","nmstart" ,"startadmin" ,"start" , "stop" , "kill"] and not self.server.machine:
			print "You have to connect to one machine to use %s" % command
			return
		if command in ["lsd" ,"lsp" ,"lswls" , "lsm" , "quit","disconnect","help"] and args :
			print "no arguments for command %s" % command
			return
		if command in ["init","nmstart" ,"startadmin" ,"start" , "stop" , "kill","use"] and not args :
			print "arguments needed run command %s" % command
			return
		self.runcmd(command,args)




cmds=["init","ls","lsd","lsm" ,"lsp" ,"lswls" ,"use","disconnect","nmstart" ,"startadmin" ,"start" , "stop" , "kill","quit","help"]

def complete(text, state):
    for cmd in cmds:
		if cmd.startswith(text):
		    if not state:
			return cmd
		    else:
			state -= 1