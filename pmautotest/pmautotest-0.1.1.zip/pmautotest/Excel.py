from xlrd import biffh
from xlrd import open_workbook
import log
import Check
import re
import ConfigParser

class Excel:


	def __init__(self):
		cf = ConfigParser.ConfigParser()
		cf.read("config.conf")		
		file_name = cf.get("EXCEL","File_name")
		self.work_book = open_workbook(file_name)
		sheet_index = cf.getint("EXCEL", "Table_sheet")
		self.table_sheet = self.work_book.sheet_by_index(sheet_index)
		self.table_col = cf.getint("EXCEL", "Table_col")			
		self.Instance_col = cf.getint("EXCEL", "Instance_col")		
		self.tag_name_col = int(cf.get("EXCEL", "tag_name_col"))
		self.range_col = int(cf.get("EXCEL", "range_col"))
		self.mLog = log.Logger("MainLog","info")
		
	def getInst(self, row):
		inst_str = str(self.table_sheet.cell(row,self.Instance_col).value)
		return inst_str
	
	def getSheetName(self, row):
		try:
			hyperlink = self.table_sheet.hyperlink_map[row,self.table_col]
		except KeyError:
			self.mLog.error("key Error:\n  Can't open current hyperlink of Excel.\nCYCLE OVER!")
			return False
		target_sheet_name = str(hyperlink.textmark)
		target = ''
		for i in target_sheet_name:
			if i == "!":
				break
			target = target + i	
		try:
			self.target_sheet = self.work_book.sheet_by_name(target)
		except biffh.XLDRError:
			pass
		return target
	

	def getTagName(self, serial_num):
		return str(self.target_sheet.cell(serial_num+2, self.tag_name_col).value)
		
	def getRangeList(self, hasRecord): #getData
		li=[]	
		col_v = 10000
		for col in range(self.target_sheet.ncols):
			if str(self.target_sheet.cell(1, col).value) == "Type":
				col_v = col
		if col_v ==10000:
			self.mLog.debug("Get data exception 3: Not Find 'type'")
		valueType = str(self.target_sheet.cell(2, col_v).value)
			
		for row in range(2, self.target_sheet.nrows):
			if row == 2:
				firstLine = self.target_sheet.cell(row,self.range_col).value 
				pattern = re.compile(r'0=')
				if pattern.search(str(firstLine)):
					if not hasRecord:
						return False
					else:
						pass
				else:
					pass
			if valueType == "Int16":
				type = self.target_sheet.cell(row, col_v).value 
				if re.match(r'Bit\d*', type ) or re.match(r'bit\d*', type ):
					self.mLog.debug("Bit Type: %s"%type)
					pass
				else:
					range_value = self.target_sheet.cell(row, self.range_col).value
					li.append(range_value)
			
			else:
				range_value = self.target_sheet.cell(row, self.range_col).value
				li.append(range_value)
		return li

	def get_data_type(self):
		col_v = 1000
		for col in range(self.target_sheet.ncols):
			if str(self.target_sheet.cell(1, col).value) == "Type":
				col_v = col
		if col_v == 1000:
			self.mLog.debug("Get data exception 3: Not Find 'type'")
		valueType = str(self.target_sheet.cell(2,col_v).value)
		self.data_type = valueType
		self.mLog.debug("Data type: %s" %valueType)
		return valueType
	
	def get_model_col(self,model_name):
		for col in range(self.table_sheet.ncols):
			if str(self.table_sheet.cell(0,col).value) == model_name:
				self.mLog.debug("Ok, I find %s in column %s !"%(model_name, col))
				self.model_col = col
				return col
			else:
				self.mLog.debug("I'm looking for Model %s, but this is %s"%(model_name,\
								str(self.table_sheet.cell(0,col).value)))		
		self.mLog.error("No model info, stop!")
			
	def model_check(self, row):		
		self.mLog.debug("Model check: %s"%str(self.table_sheet.cell(row, self.model_col).value))
		if str(self.table_sheet.cell(row, self.model_col).value) == "X":
			return False
		else:
			return True

	def getByteInfo(self):
		'''
		We need to get Start Byte and Byte Size in EXCEL file.
		For example:
		start byte is 20,byte size is 32.We put both of them into a list ,li =[20,32],for further use.		
		'''		
		li=[]
		for col in range(self.target_sheet.ncols):
			if str(self.target_sheet.cell(1, col).value) == "Start Byte":
				for row in range(2, self.target_sheet.nrows):
					aa = self.target_sheet.cell(row, col).value
					bb = self.target_sheet.cell(row, col+1).value
					if aa != ''and bb != '':
						bb = str(bb)
						li.append(bb)
				return li
				
	def size_check(self, sizeCol,row):		
		self.mLog.warning("Size check: %s"%str(self.table_sheet.cell(row, sizeCol).value))
		if row > 0:
			return self.table_sheet.cell(row, sizeCol).value
	
			