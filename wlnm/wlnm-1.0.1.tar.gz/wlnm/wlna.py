#!/usr/bin/env python

'''

wlnm.py
==========

Desc: Entry point of weblogic node agent 


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import sys
import argparse
import time

import wlnad

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Exception(message)


def main():
	
	args = None
	try:
		parser = MyArgumentParser(prog='wlna')
		parser.add_argument('command', choices=['start', 'stop','restart'], help='start|stop|restart wlnm server process')
		parser.add_argument('-p', '--port', type =int ,help='Listen port,default port is 9098',default="9098")
		args = parser.parse_args()
		if args.command == "start" and not args.port :
			raise Exception("Port is not provied when you try to start process")

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
	if args.command == "start" :
		wlnad.runDaemon(int(args.port))

	elif args.command == "stop":
		wlnad.stopDaemon()
	else:
		
		wlnad.stopDaemon()
		time.sleep(1)
		wlnad.runDaemon(int(args.port))
	
if __name__ == "__main__":
    main()