#!/usr/bin/env python

'''

wlnm.py
==========

Desc: Entry point of weblogic node master 


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import sys
import argparse

import os
import logging

import socket
import readline

import inputer,search,util

from wlnsc import ServerClient
from inputer import remoteCmds

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

 

def run(server_inst):

    print "Weblogic Node Master"
    print ""
    print "Type help to load help page ."
    print ""

    command =''
    readline.parse_and_bind("tab: complete")
    readline.set_completer(inputer.complete)
    mycmd = remoteCmds(server_inst)
    while True :
        
	
	if server_inst.machine :
		i_input = raw_input ('wlnm(%s)>>' % server_inst.machine)
	else:
		i_input = raw_input ('wlnm>>')
	if not i_input : continue
	command = i_input.split()[0]
	args=i_input.split()[1:]
	
	
	mycmd.validcmd(command,args)
	
    print "Bye"


class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Exception(message)

def main():
	#print "----"
	args = None
	try:
		parser = MyArgumentParser(prog='wlnm')
		parser.add_argument('-s', '--server' ,dest ='host', help='Hostname or IP of wlnm server,default is localhost',default="localhost")
		parser.add_argument('-p', '--port', type =int ,help='Listen port,default is 9099',default="9099")

		args = parser.parse_args()
		

	except SystemExit:
		pass
	except  Exception ,e:
		
		parser.print_help()

		print
		print "Arguments Error"
		print "---------------"
		print e
		print

		sys.exit()
	
	if not args :  sys.exit()

	if not util.checkport(args.port,host=args.host) :
			
		print " wlnm server at %s:%s is not reachable\n" % (args.host,args.port)
		sys.exit()
	

	try :
		server_inst = ServerClient(host=args.host,port=args.port)
		server_inst.connect()
		
	except Exception,e:
		print "wlnm server %s:%s is not able to connect." % (args.host,args.port)
		print
		raise e
		sys.exit()
	run(server_inst)

	

if __name__ == "__main__":
    main()
