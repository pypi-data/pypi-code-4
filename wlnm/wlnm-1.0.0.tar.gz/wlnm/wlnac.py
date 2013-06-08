
'''

wlnac.py
==========

Desc:  wlnm client to connect wlnode agent


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import xmlrpclib
import util


class agentclient():

	def __init__(self,host,port):

		self.host = host
		self.port = port
		self.conn = None


	def connect(self):
		try:
			
			self.conn = xmlrpclib.ServerProxy('http://%s:%s' % (self.host,self.port))
			self.conn.list_contents('.')

		except:
			raise Exception('not able to connect to http://%s:%s ,make sure port and host is corrected' % (self.host,self.port))


	def searchAll(self):
		return self.conn.searchAll()

	def nmstart(self,args):
		print util.decode_output(self.conn.nmstart(args))

	def startAdmin(self,args):
		print util.decode_output(self.conn.startAdmin(args))

	def startServer(self,args):
		print util.decode_output(self.conn.startServer(args))

	def stopServer(self,args):
		print util.decode_output(self.conn.stopServer(args))

	def listprocess(self):
		print util.decode_output(self.conn.listprocess())

	def kill(self,args):
		print util.decode_output(self.conn.kill(args))

	

#connect(["localhost","9099"])
#print proxy.list_contents('/tmp')