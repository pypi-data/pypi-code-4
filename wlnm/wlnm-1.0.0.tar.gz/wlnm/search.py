'''

search.py
==========

Desc: Functions for searching weblogic properties through config.xml and nodemanger.properties


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''


import os
import logging
import xml.etree.ElementTree as ET
import subprocess
import sys

import database
import util
import monitor
import wls


logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)

def get_xml_namespace(re):
	return ''.join(re.tag.split("}")[:-1])+'}'

def saveDomain(machine,domainName,domainhome,version,adminurl,user,pwd):
	
	_data = [None,None,[domainName,domainhome,version,adminurl,user,pwd],None]
	database.saveDB(machine,domain=True,data=_data)

def saveServer(machine,name,host,port,type,domain):
	_data = [None,None,None,[name,host,port,type,domain]]
	database.saveDB(machine,server=True,data=_data)

def saveWLS(machine,wlsHome,version,nmPort):
	_data = [None,[wlsHome,version,nmPort],None,None]
	database.saveDB(machine,wlss=True,data=_data)

def saveMachine(machine,port):
	_data = [port,None,None,None]
	database.saveDB(machine,mac=True,data=_data)

def searchAll():
	#print "Searching weblogic and domains on this machine ,please wait ."
	#print ""
	
	version='0.0'
	wlsresult = []
	serverresult = []
	domainresult = []

	for curdir, dirs, files in os.walk('/'):
	     if  'weblogic.jar' in files and os.path.basename(curdir) == 'lib' and os.path.basename(os.path.dirname(curdir)) == 'server':
		process = subprocess.Popen("unzip -p %s/weblogic.jar META-INF/MANIFEST.MF" % os.path.abspath(curdir),shell=True, stdout=subprocess.PIPE)
		out_str, err = process.communicate()

		for line in out_str.split('\n'):
			#print 'line is ' + line
			if 'Implementation-Version'in line :
				version =  line.split(":")[-1].strip()
		
		wls_home = os.path.abspath(os.path.join(os.path.dirname(curdir), os.pardir))

		nmPort = searchNM(wls_home)
		
		if not nmPort:
			nmPort ='NA'

		wlsresult.append((wls_home , version , nmPort))
		#saveWLS(wls_home , version , nmPort)

	

	
	for curdir, dirs, files in os.walk('/'):
	     if  'config.xml' in files and os.path.basename(curdir) == 'config' :
		  #print "domain name :%s" % os.path.basename(os.path.dirname(curdir))
		  
		  homedir = os.path.dirname(curdir)
		  
		  
		  tree = ET.parse(curdir+"/config.xml")
		  root = tree.getroot()

		  namespace = get_xml_namespace(root)
		  domainname = root.findall(".//%sname" % namespace)[0].text

		  domainversion = root.findall(".//%sdomain-version" % namespace)[0].text


		  servers = root.findall(".//%sserver" % namespace)
		  #logging.debug (servers)
		  adminserver = root.findall(".//%sadmin-server-name" % namespace)[0].text
		  user = root.findall(".//%ssecurity-configuration/%snode-manager-username" % (namespace,namespace))[0].text
		  #print user
		  enPass= root.findall(".//%ssecurity-configuration/%snode-manager-password-encrypted" % (namespace,namespace))[0].text
		  #print enPass
		  adminPort = ''
		  adminHost = ''
		  for server in servers :
			_name = server.findall(".//%sname" % namespace)[0].text
			_host = server.findall(".//%slisten-address" % namespace)[0].text
			_host = "localhost" if not _host else _host
			_port = server.findall(".//%slisten-port" % namespace)[0].text
			_type = 'A' if _name == adminserver else 'M'
			adminPort = _port if _name == adminserver else adminPort
			adminHost = _host if _name == adminserver else adminHost
			#logging.debug (_name,_host,_port,_type,domainname)
			serverresult.append((_name,_host,_port,_type,domainname))
			#saveServer(_name,_host,_port,_type,domainname)

		  adminurl = "t3://%s:%s" % (adminHost,adminPort)
		
		  #wlsHome = getwlsHome(domainversion)
		  for wlsinst in wlsresult :
			if domainversion == wlsinst[1]:
				wlsHome = wlsinst[0]
		  pwd = wls.getAdminPass(homedir,enPass,wlsHome)
		  
		  domainresult.append((domainname,homedir,domainversion,adminurl,user,pwd))

		  #saveDomain(domainname,homedir,domainversion,adminurl,user,pwd)


	#print ""
	#print "Search completed!"
	#print ""
	return wlsresult,serverresult,domainresult

def searchNM(wlsHome):
	port = ""
	with open('%s/common/nodemanager/nodemanager.properties' % wlsHome) as f:
		lines = f.read().splitlines()
		for line in lines:
			if "ListenPort" == line.split("=")[0]:
				port = line.split("=")[-1]
	f.close()
	return port			

def getMachineAgentPort(machine):
	macDB,mac = database.loadAllDB()

	for m in mac :
		if machine == m :
			return macDB[m]["agentport"]

	return
	

def getwlsHome(machine,version):

	wlsDB,wls = database.loadDB(machine,wlss=True)[0]

	for w in wls:
	    if version == wlsDB[w]["version"]:
		return wlsDB[w]["home"]
	return

def getwlsHomeByNmport(machine,port):
	
	wlsDB,wls = database.loadDB(machine,wlss=True)[0]
	wls_home = ''
	for w in wls:
	    if port == wlsDB[w]["nmport"]:
		wls_home = wlsDB[w]["home"]    

	if wls_home :
		return wls_home
	else:
		raise Exception("%s is not valid nodemanager port !" % port)

def getwls(machine,name):
	#logging.debug ("name is %s" % name)
	[wlsDB,wls],[domainsDB,domains],[serversDB,servers] = database.loadDB(machine,wlss=True,domain=True,server=True)
	version = ''
	domain = ''
	wlsHome = ''
	adminurl =''
	user = ''
	pwd = ''
	for server in servers:
		if name == serversDB[server]["name"] :
			domain = serversDB[server]["domain"]
	if domain :
		for idomain in domains:
			if domain == idomain :
				version = domainsDB[idomain]["version"]
				adminurl = domainsDB[idomain]["adminurl"]
				user = domainsDB[idomain]["user"]
				pwd = domainsDB[idomain]["pwd"]
	else:
		#print "could not find such server in local db , make sure you spell correct"
		return ('','','','')

	for key in wls:
		if version == wlsDB[key]["version"]:
			wlsHome = wlsDB[key]["home"]

	return (adminurl,wlsHome,user,pwd)	

def getDomainHome(machine,domainName):
	

	domainsDB,domains = database.loadDB(machine,domain=True)[1]
	if domainName in domains:
		return domainsDB[domainName]['home']
	else:
		return

def isWlsPort(machine,port):
	iswls = False
	[wlsDB,wls],[serversDB,servers] = database.loadDB(machine,wlss=True,server=True)[0::2]
	#print [wlsDB,wls],[serversDB,servers] 
	wls_home = ''

	for w in wls:
	    if port == wlsDB[w]["nmport"]:
		iswls = True    
	

	for server in servers:
		if port == serversDB[server]["port"] :
			iswls = True
	
	return iswls

def show(machine,args = []):
	if not args :
		showAll(machine)
	else:
		print ""
		showServers(machine,args)

def showAll(machine):
	domainsDB,domains = database.loadDB(machine,domain=True)[1]
	print ""
	for domain in domains:
	    showServers(machine,[domain])

	

def showDomains(machine):
	
	table = [["Name", "Version", "HomeDirectory","AdminURL"]]
	
	domainsDB,domains = database.loadDB(machine,domain=True)[1]
	for domain in domains:
	    table.append([domain,domainsDB[domain]["version"],domainsDB[domain]["home"],domainsDB[domain]["adminurl"]])
	    
	util.pprint_table(table)


def showServers(machine,domain):
	
	serversDB,servers = database.loadDB(machine,server=True)[2]

	for _domain in domain:
		print "[[%s]]" % _domain
		table = [["Name", "Type", "HOST/IP","PORT","STATUS"]]
		for server in servers:
			if _domain == serversDB[server]["domain"] :
				table.append([serversDB[server]["name"],serversDB[server]["type"],serversDB[server]["host"],serversDB[server]["port"],monitor.isRunning(serversDB[server]["name"])])
		    
		util.pprint_table(table)
		print ""
	
	

def showWLS(machine):
	table = [["Name", "Version", "HomeDirectory" , "NM Port","NM Status"]]
	
	
	wlsDB,wls = database.loadDB(machine,wlss=True)[0]

	_status = 'DOWN'

	for w in wls:
	    if util.checkport(wlsDB[w]["nmport"]):
		_status = 'UP'
	    table.append([w,wlsDB[w]["version"],wlsDB[w]["home"],wlsDB[w]["nmport"], _status])
	    
	util.pprint_table(table)


def showMachines():
	table = [["Machine Name", "agent port", "agent status" ]]

	macDB,mac = database.loadAllDB()
	_status = 'DOWN'

	for m in mac:
		if util.checkport(macDB[m]["agentport"]):
			_status = 'UP'
		table.append([m,macDB[m]["agentport"], _status])
	util.pprint_table(table)





'''

def checkinit(daemon):
    if not os.path.isfile(util.wlnm_data_file):
	util.creatProfileDir()
        if raw_input("For the first time use weblogic node master, it  need to gather weblogic infos on this machine , proceed [y/n] ?") == 'y' :
		#print 'Search local weblogic domains'
		searchAll()
	else:
		if daemon :
			print "If you run a daemon service must choose Y , quit now."
			print ""
			sys.exit()
		else :
			util.initDB()
			print 'Weblogic node master run as client mode ,use connect command to connect target machine.'
			print ""	
'''

#print searchNM("/bea/1035/wlserver_10.3")
#searchwls()
#showWLS()
#getwls('dsada')