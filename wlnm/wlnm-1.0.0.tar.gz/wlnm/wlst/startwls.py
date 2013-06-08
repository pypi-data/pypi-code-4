'''

startwls.py
==========

Desc: WLST script for starting remote/local managed server 


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import sys
import os
from java.lang import System
import getopt

admin_username = '';
admin_password = '';
admin_server_url ='';
server_name = '';

def usage():
    print "Usage:"
    print "wlst.sh startwls.py -u <user> -p <pass> -a <adminurl> -s <servername>"

try:
    opts, args = getopt.getopt( sys.argv[1:], "a:p:u:s:", "" )
   
    
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for opt, arg in opts:
	if opt == "-u":
		admin_username = arg
	elif opt == "-p":
		admin_password = arg
	elif opt == "-a":
		admin_server_url = arg
	elif opt == "-s":
		server_name = arg

#print '---->'+admin_username+' '+admin_password+' '+admin_server_url+' '+server_name;


print 'CONNECT TO ADMIN URL '+admin_server_url+'.......';
try:
	connect(admin_username, admin_password, admin_server_url);
except:
	print 'CAN NOT CONNECT ADMIN SERVER';


print 'STARTING WEBLOGIC SERVER  '+server_name+'.......';
try:
	start(server_name,'Server');
except:
	print 'FAIL TO STOP SERVER , IT MAY ALREADY SHUTDOWN';

