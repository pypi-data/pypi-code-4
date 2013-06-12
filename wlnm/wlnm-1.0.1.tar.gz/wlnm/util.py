'''

util.py
==========

Desc: Utils including data store , table printing ,formating and help page


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import socket
import shelve
from cStringIO import StringIO
import os
import sys
import base64





def help():
	print ">>>>>> help >>>>>>"
	print ""
	print ""
	print "lsm			List all registered machines. "
	print ""
	print "use [machineName]	use certain machine to operate. "
	print ""
	print "disconnect		disconnect current session. "
	print ""
	print "init [machineName] [agentPort]		register remote machine and gather weblogic information. "
	print ""
	print "ls [domainName]		List all weblogic domains/servers or only list one domain. "
	print ""
	print "lsd			List all weblogic domains."
	print ""
	print "lsp			List all running weblogic instances."
	print ""
	print "lswls			List all version weblogic installed on local machine."
	print ""
	print "kill [port|servername]	Kill process by port number or servername."
	print ""
	print "nmstart [port]		start weblogic node manager by port."
	print ""
	print "startadmin [domainname]	start admin server by domain name."
	print ""
	print "start [servername]	start managed server by servername."
	print ""
	print "stop [servername]	stop managed server by servername."
	print ""
	print "help			Show this page."
	print ""
	print "quit			quit weblogic node master."
	print ""
	print ""
	


#locale.setlocale(locale.LC_NUMERIC, "")
def format_num(num):
    """Format a number according to given places.
    Adds commas, etc. Will truncate floats into ints!"""

    #try:
    #    inum = int(num)
    #    return locale.format("%.*f", (0, inum), True)

    #except (ValueError, TypeError):
    return str(num)

def get_max_width(table, index):
    """Get the maximum width of the given column index"""
    return max([len(format_num(row[index])) for row in table])


def pprint_table(table):
    """Prints out a table of data, padded for alignment
    @param out: Output stream (file-like object)
    @param table: The table to print. A list of lists.
    Each row must have the same number of columns. """
    print ''

    col_paddings = []

    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))

    rownum = 0 
    for row in table:
	rownum += 1 
	if rownum == 1 :
		print '\033[1m'
        # left col
        print "%s ||" % row[0].ljust(col_paddings[0] + 1),
        # rest of the cols
        for i in range(1, len(row)):
            col = format_num(row[i]).rjust(col_paddings[i] + 2)
	    print "%s |" %col,
	
	if rownum == 1 :
		print '\033[0m'
        else:
		print


    print

def checkports(port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	for iport in port:
		print iport
		if s.connect_ex(('localhost', int(iport)))==0:
			print "port %s is Opened" % iport
			#return True
		else:
			print "port %s is Closed" % iport
			#return False
		s.close()

def checkport(port,host="localhost"):
	try :
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if s.connect_ex((host, int(port)))==0:
			#print "port %s is Opened" % iport
			return True
		else:
			#print "port %s is Closed" % iport
			return False
		s.close()
	except :
		# any wrong return false , eg. host is not resolved.
		return False

def initDB():
	db = shelve.open(wlnm_data_file,"c")
	db['local_wls'] = {}
	db['local_domains'] = {}
	db['wls_servers'] = {}
	db.close()

def loadDB(wlss=False,domain=False,server=False):
	
	db = shelve.open(wlnm_data_file, "r")
	wlsDB = None
	wls = None
	domainsDB = None
	domains = None
	serversDB = None
	servers = None

	if wlss :
		wlsDB = db['local_wls']
		wls = wlsDB.keys()
	if domain:
		domainsDB = db['local_domains']
		domains = domainsDB.keys()
	if server :
		serversDB = db['wls_servers']
		servers = serversDB.keys()
	db.close()
	return ([wlsDB,wls],[domainsDB,domains],[serversDB,servers])


def saveDB(wlss=False,domain=False,server=False,data=None):
	#print wlnm_data_file
	db = shelve.open(wlnm_data_file,"c")

	if wlss :
		wlsHome,version,nmPort = data[0]
		if 'local_wls' not in db.keys() :
			local_wls={}
		else:
			local_wls= db['local_wls']

		local_wls['wls'+version] = {"home":wlsHome,"version":version,"nmport":nmPort}
		db['local_wls']=local_wls
		#print "wls%s has been store in local db!" % version

	if domain :
		domainName,domainhome,version,adminurl,user,pwd = data[1]

		if 'local_domains' not in db.keys() :
			local_domains={}
		else:
			local_domains= db['local_domains']

		local_domains[domainName] = {"home":domainhome,"version":version,"adminurl":adminurl,"user":user,"pwd":pwd}
		db['local_domains']=local_domains
		#print "%s has been store in local db!" % domainName
	
	if server :
		name,host,port,type,domain = data[2]

		if 'wls_servers' not in db.keys() :
			wls_servers={}
		else:
			wls_servers= db['wls_servers']

		_key = "%s.%s" % (name,domain)
		wls_servers[_key] = {"name":name,"host":host,"port":port,"type":type,"domain":domain}
		db['wls_servers']=wls_servers
		#print "%s has been store in local db!" % _key

	

	db.close()



def redirectStdout():
	old_stdout = sys.stdout
	sys.stdout = mystdout = StringIO()
	return mystdout,old_stdout

def finishRedirectStdout(old_stdout):
	sys.stdout = old_stdout

def decode_output(my_out):
	return base64.b64decode(my_out)

def encode_output(my_out):
	return base64.b64encode(my_out)

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False