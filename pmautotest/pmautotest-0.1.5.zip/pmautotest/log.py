import logging
import os
class Logger:
	def __init__(self,logName,level):
		cur_path = os.path.abspath('.') + "\\log"
		if os.path.isdir(cur_path):
			pass
		else:
			os.mkdir(cur_path)
		filename = cur_path + "\\%s.log"%logName
		self.logger = logging.getLogger(logName)
		if level == "debug":
			self.logger.setLevel(logging.DEBUG)
		elif level == "info":
			self.logger.setLevel(logging.INFO)
		elif level == "warning":
			self.logger.setLevel(logging.WARNING)
		elif level == "error":
			self.logger.setLevel(logging.ERROR)
		handler = logging.FileHandler(filename,mode='w') 
		handler.setLevel(logging.NOTSET)
		formatter = logging.Formatter('%(levelname)s:%(message)s',datefmt='%Y-%m-%d %H:%M:%S')
		handler.setFormatter(formatter)
		self.logger.addHandler(handler)
    
	def log_(self,msg):
		if self.logger is not None:
			self.logger.info(msg)
	
	def debug(self,msg):
		if self.logger is not None:
			self.logger.debug(msg)
	
	def warning(self,msg):
		if self.logger is not None:
			self.logger.warning(msg)
			 
	def error(self,msg):
		if self.logger is not None:
			self.logger.error(msg)
		
def logged_class(cls,debug=False,filehandler=True):
	cur_path = os.path.abspath('.') + "\\log"
	if os.path.isdir(cur_path):
		pass
	else:
		os.mkdir(cur_path)
	filename = cur_path + "\\%s.log"%(cls.__name__)
	cls.log = logging.getLogger('{0}'.format(cls.__name__))
	if debug:
		cls.log.setLevel(logging.DEBUG)
	else:
		cls.log.setLevel(logging.WARNING)
	if filehandler:	
		handler = logging.FileHandler(filename,mode='w') 
		handler.setLevel(logging.NOTSET)
		formatter = logging.Formatter('%(name)s-%(levelname)s: %(message)s')
		handler.setFormatter(formatter)
		cls.log.addHandler(handler)
	else:
		pass