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
	'quit':sys.exit
}

cmds=cmddict.keys()


def complete(text, state):
    for cmd in cmds:
        if cmd.startswith(text):
            if not state:
                return cmd
            else:
                state -= 1
