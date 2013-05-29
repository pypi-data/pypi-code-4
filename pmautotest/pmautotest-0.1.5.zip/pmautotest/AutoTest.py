import os
import ConfigParser
import log
import re
from Check import check_validity
import Excel
import time
import socket
import threading 

class WiresnakeError(Exception):
	pass
	
def string_to_list(string_input):
	string_input = string_input.strip()
	list = string_input.split("  ")
	return list	
	
class AutoTest:
	def __init__(self):
		print "Auto Test Running ... "
		self.log.info("Cofiguring excel file...")	
		self.Library = Excel.Excel()		
		cf = ConfigParser.ConfigParser()
		cf.read("config.conf")		
		self.chan = cf.get("CIP", "Cip")
		self.model_name = cf.get("MODEL", "Model_name")
		self.Library.get_model_col(self.model_name)
		self.test_result ={}
		self.size_error = {}
		self.server()
		
	def server(self):
		HOST=''
		PORT=9999
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((HOST, PORT)) 
		self.sock.listen(5)	
		self.log.info("Configuring server ...")
				
	def table_update(self, row):
		choosed = self.Library.model_check(row)
		instance = self.Library.get_instance(row)		
		if choosed:
			self.log.info("")
			self.log.info("Update table (Inst: %s)..."%instance)
			return self.Library.update(row)			
		else:
			self.log.info("Over. %s doesn't have Instance: %s"%(self.model_name, instance))
			return	False
			
	
	def start_wiresnake_engine(self):
		tmpThread = threading.Thread(target=self.data_exchange)
		tmpThread.daemon = True
		tmpThread.start()
		time.sleep(0.1)		
		self.log.info("Starting wiresnake ...")
		os.system("wiresnake --headless --comm-driver EtherNetIP --device %s --test\
					WiresnakeEngin.py"%self.chan)							
		
	def device_update(self):
		try: 
			test = self.date_from_device
		except AttributeError:
			print "WiresnakeError! Wiresnake can't run properly.Please check network \
						connection and wiresnake."
			raise WiresnakeError			
		if self.date_from_device == "1":
			self.log.error("Data back was not among Real,Int or String.")
			return False
		if self.Library.data_type == "Real" or self.Library.data_type == "Int16":
			self.log.debug("Data from wiresnake: %s"%self.date_from_device)			
			self.date_from_device = string_to_list(self.date_from_device)			
			for value in self.date_from_device:
				if value != "0":
					return True
			self.log.info("All values are zero, ignore instance %s"%self.Library.instance)
			return False
		elif re.match(r'String\d*', self.Library.data_type):
			self.log.debug("%s"%self.date_from_device)
			return False
		else:
			self.log.error("Invalid type:%s"%self.Library.data_type)
			return	False	
		
	def data_exchange(self):
		if re.match(r'String\d*', self.Library.type):
				byte_list = self.Library.get_byte_info()
				byte_string = " ".join(byte_list)
				self.swap_info = str(self.Library.instance) + " " +\
						self.Library.type + " "+ byte_string
				self.log.info("Parmeters sending to wiresnake --> %s %s %s"\
					%(self.Library.instance, self.Library.type,byte_string))
		else:
			self.swap_info = str(self.Library.instance) + " " + self.Library.type
			self.log.info("Parmeters sending to wiresnake --> %s %s"\
					%(self.Library.instance, self.Library.type))				
		print "Connecting... "		
		newsock, address = self.sock.accept()  
		newsock.send(self.swap_info)
		self.date_from_device = newsock.recv(1024)
		newsock.close()
		self.log.info("Getting data from wiresnake...")
		
	def size_check(self):
		dev_size = len(self.date_from_device)
		table_size = self.Library.words
		table_size*=2
		if re.match(r'Int\d*', self.Library.type):
			dev_size*=2
		elif self.Library.data_type == "Real":
			dev_size*=4
		else:
			pass			
		if	dev_size!= table_size:	
			self.log.warning("Table:%s Device:%s They are not equal"%(table_size,dev_size))
			self.size_error[self.Library.instance] = "Table:%s   Device:%s "%(table_size,dev_size)
			return False
		return True

	def check(self):
		self.log.info("Checking ...")
		len_t = len(self.date_from_device)
		error_total = 0  
		for i in range(0, len_t):
			if not check_validity(self.date_from_device[i], str(self.Library.range[i]), \
					self.model_name, self.Library.instance):
				error_total += 1
				serialNum = i
				tagName = self.Library.get_tag_name(i)
				self.log.warning("")
				self.log.warning("Element Number: %s"%serialNum)
				self.log.warning("Tag: %s"%tagName)
				self.log.warning("Range: %s"%self.Library.range[i])
				self.log.warning("Value: %s"%self.date_from_device[i])
		if error_total == 0:
			self.log.info("Instance %s is All in ranges!"%self.Library.instance)
		else:
			self.test_result[self.Library.instance] = error_total
			self.log.warning("------------------------------------------------")
			self.log.warning("Totally %s error occur in instance %s\n\n"%(error_total, \
					self.Library.instance))					

	def show_result(self):
		sum = 0
		now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		version = "Version: pmautotest-0.1.3"
		self.log.warning("############### Test Result ###############")
		self.log.warning(now)
		self.log.warning("%s"%version)
		self.log.warning("Channel: %s"%self.chan)
		if self.size_error:
			self.log.warning("--- Words not equal")
			for instance in self.size_error:
				self.log.warning("%s %s"%(instance,self.size_error[instance]))
				sum += 1
		self.log.warning("--- Out of range")
		for instance in self.test_result:
			self.log.warning("%s error in instance: %s"%(self.test_result[instance],instance))
			sum += self.test_result[instance]		
		self.log.warning("################     END     ###############")
		self.log.warning("Totally %s errors found in this test."%sum)
