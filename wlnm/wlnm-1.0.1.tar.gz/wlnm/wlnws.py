#!/usr/bin/env python

'''

wlnws.py
==========

Desc: Entry point of wlnm web server


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import sys
import argparse
import time
import webserver

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Exception(message)

def main():
	
	args = None
	try:
		parser = MyArgumentParser(prog='wlnws')
		parser.add_argument('command', choices=['start', 'stop','restart'], help='start|stop|restart wlnm web server process')
		parser.add_argument('-p', '--port', type =int ,help='Listen port,default is 9100',default="9100")
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
	
	if  args.command == "start" :
		webserver.runDaemon(int(args.port))
	elif args.command == "stop":
		webserver.stopDaemon()
	else:
		webserver.stopDaemon()
		time.sleep(1)
		webserver.runDaemon(int(args.port))
	
if __name__ == "__main__":
    main()