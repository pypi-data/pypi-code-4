import os
import ConfigParser
import log
import re
from Check import check_validity
import Excel
import time
import socket
import threading 

class AutoTest:
	def __init__(self):
		print "Auto Test Run ... "
		self.mLog = log.Logger("MainLog", "debug")	
		self.autoLog = log.Logger("AutoTest", "info")
		self.sizelog = log.Logger("size", "info")
		self.mLog.log_("Cofiguring ...")
		
		self.Library = Excel.Excel()
		
		cf = ConfigParser.ConfigParser()
		cf.read("config.conf")		
		self.chan = cf.get("CIP", "Cip")
		self.model_name = cf.get("MODEL", "Model_name")
		model_col = self.Library.get_model_col(self.model_name)
		self.server()
	
	def data_exchange(self,swap_info, sock):
		print "connecting"
		newsock, address = sock.accept()  
		print "accept another connection"
		#print self.swap_info
		#data = newsock.recv(1024)   
		newsock.send(swap_info)
		global date_rv
		date_rv = newsock.recv(1024)
		newsock.close()
		
	def server(self):
		HOST=''
		PORT=9999
		self.sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((HOST, PORT)) 
		self.sock.listen(5)	
		
	def string_to_list(self,string_input):
		list = string_input.split("  ")
		return list
		
	def set_valuetype_and_instancenum(self, type, inst, target_sheet = 
										"Status_InformationTable"):
		self.data_type = type 
		inst_str = str(inst)
		self.mLog.log_("Set value (Int Real or String) and instance ...")		
		if re.match(r'String\d*', self.data_type):
			byte_list = Excel.getByteInfo(target_sheet)
			byte_string = "$".join(byte_list)
			self.swap_info = str(inst_str) + "&" + self.data_type + "&" + byte_string
			self.mLog.log_("Sent INSTANCE_NUM. and  DATA_TYPE to swap file :%s&%s&%s"%(inst_str,
				self.data_type,byte_string))
		else:
			self.swap_info = str(inst_str) + "&" + self.data_type
			self.mLog.log_("Sent INSTANCE_NUM. and  DATA_TYPE to swap file: %s&%s"%(inst_str,self.
				data_type))	
		return True
		
	def get_valuetype_and_instancenum(self, row):						
		inst_str = self.Library.getInst(row)
		self.mLog.log_("Get value (Int, Real or String) and instance number ...")
		notChoosen = self.Library.model_check(row)
		self.size = self.Library.size_check(8, row)
		if notChoosen:
			self.mLog.log_("%s doesn't have Instance: %s\nCYCLE OVER!"%(self.model_name, inst_str))
			return	False
		if inst_str == "NA":
			self.mLog.log_("NA:\nCYCLE OVER!")
			return False
		elif inst_str == "":
			self.mLog.log_("Blank:\nCYCLE OVER!")
			return False
		elif re.match(r'\D+',inst_str):
			self.mLog.log_("None digit:\nCYCLE OVER!")	
			return False
	
		else:		
			if float(inst_str) < 800:
				self.mLog.log_("Less than instance 800:\nCYCLE OVER!")
				return False
			self.Library.getSheetName(row)
			data_type = self.Library.get_data_type() 
			if not data_type:
				self.mLog.warning("Can't find data type!\nCYCLE OVER!")
				return False	
			if re.match(r'String\d*', data_type):
				byte_list = self.Library.getByteInfo()
				byte_string = "$".join(byte_list)
				self.swap_info = str(inst_str) + "&" + data_type + "&"+ byte_string
				self.mLog.log_("Instance and type is sending to swap file\
								--> %s&%s&%s"%(inst_str, data_type, byte_string))
			else:
				self.swap_info = str(inst_str) + "&" + data_type
				self.mLog.log_("Instance and type is sending to swap file\
								--> %s&%s"%(inst_str, data_type))
			self.inst_str = inst_str
			return True
			
	def get_data_from_excel(self):
		self.mLog.log_("Getting data from excel ...")
		self.excel_list = self.Library.getRangeList(int(self.Net_list[0])) 
		if self.excel_list:
			self.mLog.debug("Data from excel:")
			self.mLog.debug("\n".join(str(elem) for elem in self.excel_list))
			return self.excel_list
		else:
			self.mLog.debug("No record")
			return False
				
	def start_wiresnake_engine(self):
		tmpThread = threading.Thread(target=self.data_exchange, args=(self.swap_info,
																	self.sock))
		tmpThread.daemon = True
		tmpThread.start()
		time.sleep(0.1)
		
		self.mLog.log_("Starting wiresnake ...")
		os.system("wiresnake --headless --comm-driver EtherNetIP --device %s --test\
					WiresnakeEngin.py"%self.chan)
		  
	def get_data_from_wiresnake(self):
		self.mLog.log_("Getting data from wiresnake ...")
		attr_str = date_rv
		if attr_str == "1":
			self.mLog.warning("The data back was not among Real,Int or String.\
								\nCan't be parsed.\nCYCLE OVER!")
			return False
		self.mLog.debug("Data from wiresnake:\n %s"%attr_str)
		if self.Library.data_type == "Real" or self.Library.data_type == "Int16":
			self.Net_list = self.string_to_list(attr_str)
			return True
		elif re.match(r'String\d*', self.Library.data_type):
			self.mLog.log_("String type has not prepared")
			return False
		else:
			self.mLog.warning("Attribute invalid type:%s"%self.data_type)
			return	False
			
	def check(self):
		self.mLog.log_("Checking ...")
		self.mLog.log_("Amount of attributes from WIRESNAKE :%d"%len(self.Net_list))	
		self.mLog.log_("Amount of attributes form EXCELFILE :%d"%(len(self.excel_list)))	
		if True:
			len_t = len(self.Net_list)
			self.size*=2
			if re.match(r'Int\d*', self.Library.data_type):
				len_t*=2
			elif self.Library.data_type == "Real":
				len_t*=4
			else:
				pass
		if	len_t != self.size:	
			self.sizelog.log_("Inst:%s"%self.inst_str)
			self.sizelog.warning("Table:%s  Device:%s"%(self.size,str(len_t)))
			self.sizelog.log_("Amount of attributes from WIRESNAKE :%d\n"%len(self.Net_list))	
			
		if len(self.Net_list) > len(self.excel_list):
			len_t = len(self.excel_list)
			#self.mLog.warning("Warning! Length not equal -> Set length to: %s\n"%len_t)
			self.autoLog.log_("Inst:%s"%self.inst_str)
			self.autoLog.log_("Warning! Length not equal")
			self.autoLog.log_("Amount of attributes from WIRESNAKE :%d"%len(self.Net_list))	
			self.autoLog.log_("Amount of attributes form EXCELFILE :%d\n"%(len(self.excel_list)))
			return
		elif len(self.Net_list) < len(self.excel_list):
			len_t = len(self.Net_list)
			#self.mLog.warning("Warning! Length not equal -> Set length to: %s\n"%len_t)
			self.autoLog.log_("Inst:%s"%self.inst_str)
			self.autoLog.log_("Warning! Length not equal")
			self.autoLog.log_("Amount of attributes from WIRESNAKE :%d"%len(self.Net_list))	
			self.autoLog.log_("Amount of attributes form EXCELFILE :%d\n"%(len(self.excel_list)))
			return
		else:
			len_t = len(self.Net_list)
		error_total = 0  
		for i in range(0, len_t):
			if not check_validity(self.Net_list[i], str(self.excel_list[i]), self.model_name, self.inst_str):
				error_total += 1
				serialNum = i
				tagName = self.Library.getTagName(i)
				self.autoLog.log_("Serial number: %s\nTag name:%s"%(serialNum, tagName))
		if error_total == 0:
			self.mLog.log_("Instance %s is All in ranges!"%self.inst_str)
		else:
			self.mLog.log_("Totally %s error occur in instance %s"%(error_total, self.inst_str))
			self.autoLog.log_("------------------------------------------------")
			self.autoLog.log_("Totally %s error occur in instance %s\n\n"%(error_total, self.inst_str))
					
if __name__ == "__main__":
	a = AutoTest()
	for row in range(a.Library.table_sheet.nrows):
		a.mLog.log_("\n\n**** Starting (row:%s) ..."%row)
		if not a.get_valuetype_and_instancenum(row):
			continue
		a.start_wiresnake_engine()
		if not a.get_data_from_wiresnake():
			continue
		if not a.get_data_from_excel():
			continue
		a.check()

	
