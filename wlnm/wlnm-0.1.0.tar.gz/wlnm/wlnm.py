#!/usr/bin/env python

'''

wlnm.py
==========

Desc: Entry point of weblogic node master 


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import sys
import os
#import re
#import subprocess,shlex
import logging
import argparse
import socket
import readline

import inputer,search,util



logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')



def checkinit():
    if os.path.isfile(util.wlnm_data_file):
	#print 'initialised'
	pass
    else:
        if raw_input("For the first time use weblogic node master, it  need to gather weblogic infos on this machine , proceed [y/n] ?") == 'y' :
		#print 'Search local weblogic domains'
		util.creatProfileDir()
		search.searchAll()
	else:
		print 'Weblogic node master terminated .'
		print ""
		sys.exit(0)

def runcmd(command,args):
	if command not in inputer.cmddict.keys():
		print 'Invilad command! Press Tab key or use help command list all avaiable command.'
		print ''
	else:
		if not args:
			inputer.cmddict[command]()
		else:
			inputer.cmddict[command](args)





def main():
    print ""
    checkinit()
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-n', '--new', help='creates a new object')

    #util.help()
    print "Weblogic Node Master"
    print ""
    print "Type help to load help page ."
    print ""

    command =''
    readline.parse_and_bind("tab: complete")
    readline.set_completer(inputer.complete)
    while command is not 'quit' :
	i_input = raw_input ('%s>>' % socket.gethostname())
	if not i_input : continue
	command = i_input.split()[0]
	args=i_input.split()[1:]
	runcmd(command,args)
    print "Bye"


if __name__ == "__main__":
    main()
