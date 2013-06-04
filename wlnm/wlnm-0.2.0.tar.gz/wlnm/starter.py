'''

starter.py
==========

Desc: AdminServer and node manager process admin command including start and kill


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''


import subprocess
import psutil

import search
import util

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def startAdmin(domain):
	for domain_str in domain:
		_domain = search.getDomain(domain_str)

		if _domain is not None :
			domainhome = _domain['home']
			proc = subprocess.Popen('nohup %s/startWebLogic.sh 1>>/dev/null 2>&1 &' % domainhome, shell=True, stdout=subprocess.PIPE)
			#out, err = proc.communicate()
			#print out
			print "server process starting "
		else :
			print "%s not exist , please check name or reinit" % domain_str
			return

def kill(args):
	for arg in args:
		if RepresentsInt(arg):
			killbyport(arg)
		else:
			killbyname(arg)

def killbyname(name):
	for p in psutil.process_iter():
			for subcmd in p.cmdline :
				if '-Dweblogic.Name=' in subcmd and name == subcmd.split("=")[-1]:
					p.kill()
					print "%s is stopped!" % name

def killbyport(port):
	 pid = ''
	 if not isWlsPort(port):
		print "%s:Not a valid weblogic port !" % port
		return
	 cmd_str = "netstat -pan 2>/dev/null|grep %s|grep LISTEN|tr -s ' ' '/' |cut -f7 -d '/'|tail -1" % port
	 p = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE)
	 pid = p.communicate()[0].strip()

	 if RepresentsInt(pid):
		 proc = psutil.Process(int(pid))
		 proc.kill()
		 print "process listen on %s is killed ." % port
	 else:
		print "no process listen on %s!" % port

def nmstart(port):
	_port = port[0]
	wlsDB,wls = util.loadDB(wlss=True)[0]
	wls_home = ''
	for w in wls:
	    if _port == wlsDB[w]["nmport"]:
		wls_home = wlsDB[w]["home"]    

	if wls_home :
		cmd_str = 'nohup %s/server/bin/startNodeManager.sh 1>/dev/null 2>&1 &' % wls_home
		runcmd(cmd_str)
	else:
		print "%s is not valid nodemanager port !" % port

def runcmd(cmd_str):
	proc = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE)
	#while proc.poll() is None:
	    #output = proc.stdout.readline()
	    #print output
	print "Nodemanager started."

def isWlsPort(port):
	iswls = False
	[wlsDB,wls],[serversDB,servers] = util.loadDB(wlss=True,server=True)[0::2]
	#print [wlsDB,wls],[serversDB,servers] 
	wls_home = ''

	for w in wls:
	    if port == wlsDB[w]["nmport"]:
		iswls = True    
	

	for server in servers:
		if port == serversDB[server]["port"] :
			iswls = True
	
	return iswls