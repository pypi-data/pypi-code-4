'''

agent.py
==========

Desc: agent facade ,  remote call interface


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 


'''

import traceback

import util
import search
import starter
import monitor
import wls

def searchAll():
	
	return search.searchAll()
	


def nmstart(wls_home):
	mystdout,old_stdout = util.redirectStdout()
	try:
		starter.nmstart(wls_home)
	except :
		traceback.print_exc()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def startAdmin(domainhome):
	mystdout,old_stdout = util.redirectStdout()
	try:
		starter.startAdmin(domainhome)
	except :
		traceback.print_exc()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def startServer(args):
	mystdout,old_stdout = util.redirectStdout()
	try:
		wls.startServer(args)
	except :
		traceback.print_exc()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def stopServer(args):
	mystdout,old_stdout = util.redirectStdout()
	try:
		wls.stopServer(args)
	except :
		traceback.print_exc()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def listprocess():
	mystdout,old_stdout = util.redirectStdout()
	try:
		monitor.listprocess()
	except :
		traceback.print_exc()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def kill(args):
	mystdout,old_stdout = util.redirectStdout()
	try:
		starter.kill(args)
	except :
		traceback.print_exc()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())


