#!/usr/bin/env python

import sys
import argparse

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise Exception(message)

def main():

	try:
		parser = ThrowingArgumentParser(prog='wlnm',epilog="Weblogic node master , a command tool to manage weblogic easily")
		#parser = argparse.ArgumentParser
		group = parser.add_mutually_exclusive_group()
		parser.add_argument('command', choices=['start', 'stop', 'connect'], help='start|stop|connect')
		group.add_argument('-s',  dest='server', default=False, help='Run weblogic node server')
		group.add_argument('-a', '--agent', action="store_true", dest='agent', help='Run weblogic node agent')
		parser.add_argument('-p', '--port', type =int ,help='Listen port',required=True)
		args = parser.parse_args()

	except SystemExit:
		pass
	except  Exception ,e:
		print
		print e
		print
		parser.print_help()
		
	
	

if __name__ == "__main__":
    main()