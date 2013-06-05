__author__ = 'chenxm'

import os
import subprocess
import glob
import time
import traceback
from py4j.java_gateway import JavaGateway
from py4j.java_collections import MapConverter, ListConverter


class DetectRight(object):

	def __init__(self, dbstring):
		self.db = dbstring
		if not os.path.exists(self.db):
			raise IOError, "Invalid detectright database: %s" % self.db
		self.pid = None		

	def start_server(self):
		# prepare variables about java module of pyDetectRight
		java_folder = os.path.join(os.path.dirname(__file__), 'java')
		java_src = os.path.join(java_folder, 'src')
		java_lib = os.path.join(java_folder, 'lib')
		if os.name == 'win32':
			java_bin = "C:/pydetectright/bin"
		else:
			java_bin = '/tmp/pydetectright/bin'
		if not os.path.exists(java_bin): os.makedirs(java_bin)
		# CLASSPATH for java
		if not os.environ.has_key("CLASSPATH"):
			print("warnning: environment variable 'CLASSPATH' is emtpy")
		classpath = os.environ["CLASSPATH"] if os.environ.has_key("CLASSPATH") else ''
		classpath += (".:" + java_bin + ':')
		for lib_jar in glob.glob(os.path.join(java_lib, '*.jar')):
			classpath = ''.join([os.path.join(java_lib, lib_jar), ':', classpath])
		# JAVA_HOME
		javahome = os.environ.get("JAVA_HOME")
		# compile java module
		compile_cmd = os.path.join(javahome, 'bin/javac') if javahome else 'javac'
		compile_cmd = ' '.join([compile_cmd, '-d', java_bin, '-cp', classpath, os.path.join(java_src, 'omnilab/bd/chenxm/DetectRightEntry.java')])
		pc = subprocess.Popen(compile_cmd, shell = True); pc.wait()
		# run gateway server
		run_cmd = os.path.join(javahome, 'bin/java') if javahome else 'java'
		run_cmd = ' '.join([run_cmd, '-cp', classpath, 'omnilab.bd.chenxm.DetectRightEntry'])
		pr = subprocess.Popen(run_cmd, shell = True, preexec_fn=os.setsid)
		self.pid = pr.pid
		time.sleep(5)	# wait for starting gateway server
		try:
			self.gateway = JavaGateway()
			self.entry = self.gateway.entry_point
			self.gateway.entry_point.initializeDetectRight(self.db)
		except:
			print traceback.format_exc()
			self.stop_server()


	def stop_server(self):
		import signal
		print("Stopping server...")
		# Send the signal to all the process groups
		if self.pid: os.killpg(self.pid, signal.SIGTERM)


	def getAllDevices(self, ids = None):
		devmap = None
		if ids == None:
			devmap = self.entry.getAllDevices()
		else:
			java_list = ListConverter().convert(ids, self.gateway._gateway_client)
			devmap = self.entry.getAllDevices(java_list)
		return devmap


	def getProfile(self, schema = None):
		if schema is None:
			return self.entry.getProfile()
		else:
			return self.entry.getProfile(schema)


	def getProfileFromDevice(self, entitytype, category, description):
		return self.entry.getProfileFromDevice(entitytype, category, description)


	def getProfileFromDeviceID(self, id):
		return self.entry.getProfileFromDeviceID(id)


	def getProfileFromHeaders(self, lhm):
		java_map = MapConverter().convert(lhm, self.gateway._gateway_client)
		return self.entry.getProfileFromHeaders(java_map)


	def getProfileFromPhoneID(self, id):
		return self.entry.getProfileFromPhoneID(str(id))


	def getProfileFromTAC(self, tac):
		return self.entry.getProfileFromTAC(tac)


	def getProfileFromUA(self, ua):
		return self.entry.getProfileFromUA(ua)


	def getProfileFromUAProfile(self, uap):
		return self.entry.getProfileFromUAProfile(uap)
