'''

database.py
==========

Desc: Functions for db persistense


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''
import shelve
import os
from os.path import expanduser

wlnm_data_file = "%s/.wlnm/wlnm.dat" % expanduser("~")


def creatProfileDir():
	pdir = "%s/.wlnm" % expanduser("~")
	if not os.path.exists(pdir):
		os.makedirs(pdir,0700)


def checkdb():
    if not os.path.isfile(wlnm_data_file):
	creatProfileDir()
        initDB()

def initDB():
	db = shelve.open(wlnm_data_file,"c")
	db['wlnm'] = {}
	db.close()

def loadAllDB():
	db = shelve.open(wlnm_data_file, "r")
	wlnmDB = db['wlnm']
	machines = wlnmDB.keys()
	return ((wlnmDB,machines))

def loadDB(machine,wlss=False,domain=False,server=False):
	
	db = shelve.open(wlnm_data_file, "r")
	wlsDB = None
	wls = None
	domainsDB = None
	domains = None
	serversDB = None
	servers = None

	if wlss :
		wlsDB = db['wlnm'][machine]['wls']
		wls = wlsDB.keys()
	if domain:
		domainsDB = db['wlnm'][machine]['domains']
		domains = domainsDB.keys()
	if server :
		serversDB = db['wlnm'][machine]['servers']
		servers = serversDB.keys()
	db.close()
	return ([wlsDB,wls],[domainsDB,domains],[serversDB,servers])


def saveDB(machine,mac=False,wlss=False,domain=False,server=False,data=None):
	#print wlnm_data_file
	db = shelve.open(wlnm_data_file,"c")
	alldata = db['wlnm']
	if mac :
		port = data[0]
		alldata[machine] = {"agentport":port,"wls":{},"domains":{},"servers":{}}

	if wlss :
		wlsHome,version,nmPort = data[1]
		alldata[machine]['wls']['wls'+version] = {"home":wlsHome,"version":version,"nmport":nmPort}
		#print "wls%s has been store in local db!" % version

	if domain :
		domainName,domainhome,version,adminurl,user,pwd = data[2]

		alldata[machine]['domains'][domainName] = {"home":domainhome,"version":version,"adminurl":adminurl,"user":user,"pwd":pwd}
		#print "%s has been store in local db!" % domainName
	
	if server :
		name,host,port,type,domain = data[3]

		_key = "%s.%s" % (name,domain)
		alldata[machine]['servers'][_key] = {"name":name,"host":host,"port":port,"type":type,"domain":domain}
		
		#print "%s has been store in local db!" % _key

	db['wlnm']=alldata

	db.close()

