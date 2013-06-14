#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from config import *

class ProfileManager:
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:  
			cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)  
		return cls._instance

	def getProfileByAppName(self, appName):
		#TODO 未来可能不同的app对应不同的Profile
	 	result = {
		 			"name":'\"PROVISIONING_PROFILE[sdk={}]\"'.format(self.getSDKType()),
		 			"hash":'\"77DECEE6-E3E4-4429-B986-DD6AC8948F9C\"'
	 			}
		return result

	def getProfileByAppNameAndBuildType(self, appName, buildType):
		#TODO 不同的build类型，daily RC 渠道包 APP_STORE
	 	result = {
		 			"name":'\"PROVISIONING_PROFILE[sdk={}]\"'.format(self.getSDKType()),
		 			"hash":'\"77DECEE6-E3E4-4429-B986-DD6AC8948F9C\"'
	 			}
		return result

	def getSDKType(self):
		return "iphoneos*"