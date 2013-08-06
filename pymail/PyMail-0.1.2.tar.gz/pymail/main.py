'''
Module main
===========

Contains the main program
'''

import sys
import server

def main():
    '''
    Main program (called by shell command)
    '''
    try:
        serv = server.Server(sys.argv[1:])
        serv.start()
    except server.InitError as e:
        print 'ERROR:', e
