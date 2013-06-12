#!/usr/bin/env python

'''

wlns.py
==========

Desc: Entry point of weblogic node server


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import sys
import argparse
import time

import wlnsd

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Exception(message)

def main():
	
	args = None
	try:
		parser = MyArgumentParser(prog='wlns')
		#parser = argparse.ArgumentParser
		parser.add_argument('command', choices=['start', 'stop','restart'], help='start|stop|restart wlnm server process')
		parser.add_argument('-p', '--port', type =int ,help='Listen port,default is 9099',default="9099")
		args = parser.parse_args()
		if args.command == "start" and not args.port :
			raise Exception("Port is not provied when you try to start server")

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
	
	if  args.command == "start" :
		wlnsd.runDaemon(int(args.port))
	elif args.command == "stop":
		wlnsd.stopDaemon()
	else:
		wlnsd.stopDaemon()
		time.sleep(1)
		wlnsd.runDaemon(int(args.port))
	
if __name__ == "__main__":
    main()