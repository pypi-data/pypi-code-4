'''

inputer.py
==========

Desc: Helper module for command which user typed


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import sys
import readline

import search
import starter
import monitor
import wls
import util
import wlnmc
from wlnmd import wlnmDaemon


remote = False

cmddict={'init':search.searchAll,
	'ls':search.show,
	'lswls':search.showWLS,
	'lsd':search.showDomains,
	'nmstart':starter.nmstart,
	#'checkport':util.checkport,
	'help':util.help,
	'startadmin':starter.startAdmin,
	'start':wls.startServers,
	'stop':wls.stopServers,
	'lsp':monitor.listprocess,
	'kill':starter.kill,
	'connect':wlnmc.connect,
	'quit':sys.exit
}

remote_cmddict={'init':wlnmc.searchAll,
	'ls':wlnmc.show,
	'lswls':wlnmc.showWLS,
	'lsd':wlnmc.showDomains,
	'nmstart':wlnmc.nmstart,
	'help':util.help,
	'startadmin':wlnmc.startAdmin,
	'start':wlnmc.startServers,
	'stop':wlnmc.stopServers,
	'lsp':wlnmc.listprocess,
	'kill':wlnmc.kill,
	'connect':wlnmc.connect,
	'disconnect':wlnmc.disconnect,
	'quit':sys.exit
}

cmds=cmddict.keys()

rcmds = remote_cmddict.keys()

def complete(text, state):
    if remote :
	for cmd in rcmds:
		if cmd.startswith(text):
		    if not state:
			return cmd
		    else:
			state -= 1
    else:
	for cmd in cmds:
		if cmd.startswith(text):
		    if not state:
			return cmd
		    else:
			state -= 1

def validcmd(command,args,remote):
	if command in ["lsd" ,"lsp" ,"lswls" , "init" , "quit","disconnect","help"] and args :
		print "no arguments for command %s" % command
		return
	if command in ["nmstart" ,"startadmin" ,"start" , "stop" , "kill","connect"] and not args :
		print "arguments needed run command %s" % command
		return
	runcmd(command,args,remote)

def runcmd(command,args,remote):
	
	if remote :
		icmddict = remote_cmddict
	else :
		icmddict = cmddict

	if command not in icmddict.keys():
		print 'Invilad command! Press Tab key or use help command list all avaiable command.'
		print ''
	else:
		if not args :
			if command == "ls" :
				icmddict[command]([])
			else :
				icmddict[command]()
		else:
			icmddict[command](args)
