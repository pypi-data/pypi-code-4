#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, re, sys
from config import *

class AppManager:
	_instance = None
	def __new__(cls, *args, **kwargs):
		if not cls._instance:  
			cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)  
		return cls._instance

	def __init__(self):
		pass

	def getPublishPathByAppName(self, appName):
		if appName in map_appname_path:
			return map_appname_path[appName]
		else:
			print "{} not in map_appname_path".format(appName)
			sys.exit(1)

	def getAppName(self):
		return self.getAppNameByRespName(
				self.getRespNameByAppPath(
						self.getCurrentPath()
					)
			)

	def getAppNameByRespName(self,respName):
		if respName in map_resp_appname:
			return map_resp_appname[respName]
		else:
			print "{} not in map_resp_appname".format(respName)
			sys.exit(1)

	def getRespNameByAppPath(self,path):
		sOriginPath = self.getCurrentPath()
		os.chdir(path)
		#若匹配“remote.*url”有多行，则获取最后一行的最后一个‘/’后面的字符串
		resp_path = os.popen("git config -l|grep -p 'remote.*url='|awk -F'=' '{print $2}'").read()
		respName = re.sub(r'[\r\n]','',re.split('/', resp_path)[-1])
		os.chdir(sOriginPath)
		return respName

	def getCurrentPath(self):
		return os.getcwd()

	def getBuildAppPath(self):
		sPath = 'build/Release-iphoneos/'
		sCommand = "find {} -name \"*.app\"".format(sPath)
		sBuildAppPath = easySys(sCommand)
		return sBuildAppPath