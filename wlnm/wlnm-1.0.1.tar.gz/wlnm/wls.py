
'''

wls.py
==========

Desc: WLST proxy module to invoke WLST script 


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import subprocess
import logging
import os
import search

logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

WLSTPATH = os.path.dirname(search.__file__)

def startServers(namelist):
	logging.debug ("namelist is %s" % namelist)
	for name in namelist:
		startServer(name)


def startServer(args):

	(adminurl,wlsHome,user,pwd,name) = args
	logging.debug ("name is %s" % name)
	flag = False
	
	
	cmd_str = '%s/common/bin/wlst.sh %s/wlst/startwls.py -u %s -p %s -a %s -s %s' % (wlsHome,WLSTPATH,user,pwd,adminurl,name)
	proc = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE)
	
	print "%s starting request has been sent , will be in running status shortly. " % name
	'''
	# not print output in this way ,as start may takes time
	while proc.poll() is None:
	    output = proc.stdout.readline()
	    if output.startswith('CONNECT TO ADMIN URL') or flag:
		flag = True
	    if flag:
		print output
	'''

	

def stopServers(namelist):
	logging.debug ("namelist is %s" % namelist)
	for name in namelist:
		stopServer(name)

def stopServer(args):
	(adminurl,wlsHome,user,pwd,name) = args
	logging.debug ("name is %s" % name)
	
	flag = False
	
	cmd_str = '%s/common/bin/wlst.sh %s/wlst/stopwls.py -u %s -p %s -a %s -s %s' % (wlsHome,WLSTPATH,user,pwd,adminurl,name)
	proc = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE)
	while proc.poll() is None:
	    output = proc.stdout.readline()
	    if output.startswith('CONNECT TO ADMIN URL') or flag:
		flag = True
	    if flag:
		print output





def getAdminPass(domainhome,encryptpass,wlsHome):
	
	result = ''
	cmd_str = '%s/common/bin/wlst.sh %s/wlst/decryptPass.py %s %s' % (wlsHome,WLSTPATH,domainhome,encryptpass)
	proc = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE)
	while proc.poll() is None:
	    _tmp = proc.stdout.readline()
	    result = _tmp if _tmp else result
	    #print _tmp
	return result.strip()

	
#print getAdminPass('/beavar/1035/domains/wlsd_poc_local','{AES}wFHEVrsOI5zYvqadICOAqkOZghorXgTMJ79jiGufnIY=','/bea/1035/wlserver_10.3')