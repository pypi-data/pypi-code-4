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

import inputer,search,wlnmd,wlnmc



logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')


def local_run():

    print "Weblogic Node Master"
    print ""
    print "Type help to load help page ."
    print ""

    command =''
    #remoteCMD = False
    readline.parse_and_bind("tab: complete")
    while True :
        #remoteCMD = inputer.remote
	readline.set_completer(inputer.complete)
	if inputer.remote :
		i_input = raw_input ('%s>>' % wlnmc.host)
	else:
		i_input = raw_input ('%s(localhost)>>' % socket.gethostname())
	if not i_input : continue
	command = i_input.split()[0]
	args=i_input.split()[1:]
	inputer.validcmd(command,args,inputer.remote)
	
	'''
	if command == "connect" :
		remoteCMD = True
	if command == "disconnect" :
		remoteCMD = False
	'''
    print "Bye"



def main():
    print 
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--daemon', action="store_true" , dest='daemon', default=False, help='Run wlnm in daemon mode')
    parser.add_argument('-p', '--port', dest='listenPort', help='Listen port to run wlnm as daemon')
    parser.add_argument('-k', '--kill', action="store_true", dest='killwlnmd', help='Kill wlnm daemon process')
    args = parser.parse_args()
    
    if args.daemon or args.killwlnmd :
	search.checkinit(True)
    else :
	search.checkinit(False)
    
    if  args.daemon:
	if args.listenPort :
		#print args.listenPort 
		
		wlnmd.runDaemon(int(args.listenPort))
	else:
		print "Port number need to provide , eg. -p 9099 or --port 9099"
	
    elif  args.killwlnmd:
	wlnmd.stopDaemon()
    else :
	local_run()


if __name__ == "__main__":
    main()
