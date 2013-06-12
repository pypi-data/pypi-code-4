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



def startAdmin(domainhome):
	
	proc = subprocess.Popen('nohup %s/startWebLogic.sh 1>>/dev/null 2>&1 &' % domainhome, shell=True, stdout=subprocess.PIPE)
	#out, err = proc.communicate()
	#print out
	print "Admin server process starting "

def kill(args):
	arg = args[0]
	if util.RepresentsInt(arg):
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
	 
	 cmd_str = "netstat -pan 2>/dev/null|grep %s|grep LISTEN|tr -s ' ' '/' |cut -f7 -d '/'|tail -1" % port
	 p = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE)
	 pid = p.communicate()[0].strip()

	 if util.RepresentsInt(pid):
		 proc = psutil.Process(int(pid))
		 proc.kill()
		 print "process listen on %s is killed ." % port
	 else:
		print "no process listen on %s!" % port

def nmstart(wls_home):
	cmd_str = 'nohup %s/server/bin/startNodeManager.sh 1>/dev/null 2>&1 &' % wls_home
	runcmd(cmd_str)

def runcmd(cmd_str):
	#print cmd_str
	proc = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE)
	#while proc.poll() is None:
	    #output = proc.stdout.readline()
	    #print output
	print "Nodemanager started."

