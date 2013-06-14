#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, datetime, re
from config import *

class VersionManager:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:  
			cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)  
		return cls._instance

	def getCurVer(self):
		return "{}_{}_{}".format(self.getType(),self.getDate(),self.getTodayVersion())

	def getType(self):
		# rc daily real store
		return "daily"

	def getDate(self):
		today = datetime.date.today()
		return today.strftime('%Y%m%d')

	def getTodayVersion(self):
		return re.sub(r'[\r\n]','',os.popen("git rev-parse --short HEAD").read())