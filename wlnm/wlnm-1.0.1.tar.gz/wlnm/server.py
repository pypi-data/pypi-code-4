'''

server.py
==========

Desc: server facade ,  remote call interface


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 


'''

import util
import search
from wlnac import agentclient
import traceback

def showMachines():

	mystdout,old_stdout = util.redirectStdout()
	search.showMachines()
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def initMachine(machine, port):

	try:
		agent = agentclient(host=machine,port=port)
		agent.connect()
		wlss,servers,domains = agent.searchAll()
		search.saveMachine(machine,port)
		
		for wls in wlss :
			search.saveWLS(machine,*wls)
		for server in servers :
			search.saveServer(machine,*server)
		for domain in domains :
			search.saveDomain(machine,*domain)

		return "%s initialise successfully." % machine
	except:
		traceback.print_exc()
		return "%s initialise failed." % machine

def useMachine(args):
	machine = args[0]
	try:
		
		port = search.getMachineAgentPort(machine)
		if  not port:
			return "%s is not initiliased , please use init commmand first. " % machine
		else :
			return port
	except:
		traceback.print_exc()
		return "wlnm server fail, check server log."

def show(args):
	mystdout,old_stdout = util.redirectStdout()
	machine = args[0]
	search.show(machine,args[1:])
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def showWLS(machine):
	mystdout,old_stdout = util.redirectStdout()
	search.showWLS(machine)
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def showDomains(machine):
	mystdout,old_stdout = util.redirectStdout()
	search.showDomains(machine)
	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def nmstart(args):
	mystdout,old_stdout = util.redirectStdout()
	machine = args[0]
	nmport = args[1]
	port = search.getMachineAgentPort(machine)
	try:
		wls_home = search.getwlsHomeByNmport(machine,nmport)
		
		agent = agentclient(host=machine,port=port)
		agent.connect()
		agent.nmstart(wls_home)
		print ""
	except Exception as e:
		traceback.print_exc()
		print "nmstart invoke failed on %s " % machine
		print e


	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def startAdmin(args):
	mystdout,old_stdout = util.redirectStdout()
	machine = args[0]
	domain = args[1]
	domainhome = ''
	port = search.getMachineAgentPort(machine)
	try:
		domainhome = search.getDomainHome(machine,domain)
		if not domainhome :
			raise Exception("%s is not resigtered !" % domain)
		agent = agentclient(host=machine,port=port)
		agent.connect()
		agent.startAdmin(domainhome)
		print ""
	except Exception as e:
		traceback.print_exc()
		print "startAdmin invoke failed on %s " % machine
		print e

	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def startServer(args):
	mystdout,old_stdout = util.redirectStdout()
	machine = args[0]
	servername = args[1]
	port = search.getMachineAgentPort(machine)
	try:
		(adminurl,wlsHome,user,pwd) = search.getwls(machine,servername)
		if not wlsHome :
			raise Exception("could not find %s , make sure you spell correct" % name)
		agent = agentclient(host=machine,port=port)
		agent.connect()
		agent.startServer((adminurl,wlsHome,user,pwd,servername))
		print ""
	except Exception as e:
		traceback.print_exc()
		print "startServers invoke failed on %s " % machine
		print e

	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def stopServer(args):
	mystdout,old_stdout = util.redirectStdout()
	machine = args[0]
	servername = args[1]
	port = search.getMachineAgentPort(machine)
	try:
		(adminurl,wlsHome,user,pwd) = search.getwls(machine,servername)
		if not wlsHome :
			raise Exception("could not find %s , make sure you spell correct" % name)
		agent = agentclient(host=machine,port=port)
		agent.connect()
		agent.stopServer((adminurl,wlsHome,user,pwd,servername))
		print ""
	except Exception as e:
		traceback.print_exc()
		print "stopServers invoke failed on %s " % machine
		print e

	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def listprocess(machine):
	mystdout,old_stdout = util.redirectStdout()
	port = search.getMachineAgentPort(machine)
	try:
		agent = agentclient(host=machine,port=port)
		agent.connect()
		agent.listprocess()
		print ""
	except:
		traceback.print_exc()
		print "listprocess invoke failed on %s " % machine

	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())

def kill(args):
	mystdout,old_stdout = util.redirectStdout()
	machine = args[0]
	port = search.getMachineAgentPort(machine)
	try:
		# check arg
		
		if util.RepresentsInt(args[1]):
			if not search.isWlsPort(machine,args[1]) :
				raise Exception ("%s is not a valid weblogic port" % args[1])
			
		
		agent = agentclient(host=machine,port=port)
		agent.connect()
		agent.kill(args[1:])
		
		print ""
	except Exception as e:
		traceback.print_exc()
		print "kill invoke failed on %s " % machine
		print e

	util.finishRedirectStdout(old_stdout)
	return util.encode_output(mystdout.getvalue())


''' not for remote call '''
'''
def getAgent(host,port):
	try:
		agent = agentclient(host=host,port=port)
		agent.connect()

		return agent
	except:
		return
'''


