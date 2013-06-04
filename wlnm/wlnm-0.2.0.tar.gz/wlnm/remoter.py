'''

remoter.py
==========

Desc: process function proxy for remote call


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 


'''

import util
import search
import starter
import monitor
import wls

def searchAll():
	mystdout,old_stdout = util.redirectStdout()
	search.searchAll()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def show(args):
	mystdout,old_stdout = util.redirectStdout()
	search.show(args)
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def showWLS():
	mystdout,old_stdout = util.redirectStdout()
	search.showWLS()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def showDomains():
	mystdout,old_stdout = util.redirectStdout()
	search.showDomains()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def nmstart(args):
	mystdout,old_stdout = util.redirectStdout()
	starter.nmstart(args)
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def startAdmin(args):
	mystdout,old_stdout = util.redirectStdout()
	starter.startAdmin(args)
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def startServers(args):
	mystdout,old_stdout = util.redirectStdout()
	wls.startServers(args)
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def stopServers(args):
	mystdout,old_stdout = util.redirectStdout()
	wls.stopServers(args)
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def listprocess():
	mystdout,old_stdout = util.redirectStdout()
	monitor.listprocess()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def kill(args):
	mystdout,old_stdout = util.redirectStdout()
	starter.kill(args)
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())


