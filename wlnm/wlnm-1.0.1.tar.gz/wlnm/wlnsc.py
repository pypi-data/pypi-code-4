
'''

wlnsc.py
==========

Desc:  wlnm client to connect wlnode server


Author: Kevin Yi<yikaus @ gmail>

License  : BSD 

'''

import xmlrpclib
import util
import inputer
import sys

class ServerClient():

	def __init__(self,host,port):

		self.host = host
		self.port = port
		self.conn = None
		self.machine = None
		self.aPort = port

	def connect(self):
		try:
			self.conn = xmlrpclib.ServerProxy('http://%s:%s' % (self.host,self.port))
			
			self.conn.list_contents('.')
			

		except:
			#print 'not able to connect to http://%s:%s ,make sure port and host is corrected' % (self.host,self.port)
			message = 'Having trouble to communicate with wlnm server %s:%s ,you may need to restart it \n'
                        sys.stderr.write(message % (self.host,self.port))
                        sys.exit(1)

	def setMachine(self,args):
		self.machine = args[0]
		
		result =self.conn.useMachine(args)
		try:
			self.aPort = int(result)
			
		except:
			print result


	def disconnect(self):
		self.machine = None
		self.aPort = None
	
	def showMachines(self):
		print util.decode_output(self.conn.showMachines())
	
	def initMachine(self,args):
		print  self.conn.initMachine(args[0], args[1])

	def show(self,args):
		args.insert(0,self.machine)
		print util.decode_output(self.conn.show(args))

	def showWLS(self):
		print util.decode_output(self.conn.showWLS(self.machine))

	def showDomains(self):
		print util.decode_output(self.conn.showDomains(self.machine))

	def nmstart(self,args):
		args.insert(0,self.machine)
		print util.decode_output(self.conn.nmstart(args))

	def startAdmin(self,args):
		args.insert(0,self.machine)
		print util.decode_output(self.conn.startAdmin(args))

	def startServer(self,args):
		args.insert(0,self.machine)
		print util.decode_output(self.conn.startServer(args))

	def stopServer(self,args):
		args.insert(0,self.machine)
		print util.decode_output(self.conn.stopServer(args))

	def listprocess(self):
		print util.decode_output(self.conn.listprocess(self.machine ))

	def kill(self,args):
		args.insert(0,self.machine)
		print util.decode_output(self.conn.kill(args))

	


#s = ServerClient(host="localhost",port="8088")
#s.connect()