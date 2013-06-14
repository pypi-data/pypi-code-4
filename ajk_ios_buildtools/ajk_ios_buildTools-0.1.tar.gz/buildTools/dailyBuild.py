#!/usr/bin/python
# -*- coding: utf-8 -*-
import json, httplib, urllib, sys, os, re, argparse
from versionManager import *
from profileManager import *
from deviceManager import *
from appManager import *
from config import *

def dailyBuild():
	sBathPath = "."

	###prepare params
	#版本号，用于水印，以及info.plist中
	sDayVer = VersionManager().getCurVer()
	#每个APP的AppDelegate.m中设置的 [[RTRequestProxy sharedInstance] setAppName:xxxx];
	sAppName = AppManager().getAppName()
	#Provioning Profile文件名，字典类型，d => "dictionary"
	dProfile = ProfileManager().getProfileByAppName(sAppName)

	#可不设置，默认会build当前目录下的xcodeproj文件以及第一个target
	#sProjName = "AiFang.xcodeproj"
	sTargetIpaName = sAppName + "_" + sDayVer

	#-configuration 默认Debug 或 Release
	sConf = "Release"

	###xcodebuild shell puzzle
	sShell = "xcodebuild"
	#if len(sProjName) > 0:
	#	sShell += ' -project {}'.format(sProjName)
	#if len(sTarget) > 0:
	#	sShell += ' -target {}'.format(sTarget)
	if len(sConf) > 0:
		sShell += ' -configuration {}'.format(sConf)
	if 'name' in dProfile:
		sShell += ' {}={}'.format(dProfile["name"],dProfile["hash"])
	sShell += ' OBJROOT={0}/build SYMROOT={0}/build'.format(sBathPath)
	sShell += ' clean build'
	os.chdir(sBathPath)
	#print sShell
	# sys.exit()
	result = os.system(sShell)
	if 0 != result:
		print "Build failed"
	else:
		print "\n\n\n\033[0;31m打包成功\n\n\n"

	###xcrun PackageApplication puzzle
	sShellXcrun = 'xcrun -sdk iphoneos PackageApplication -v'
	sAppPath = AppManager().getBuildAppPath()
	sOutPutFile = '~/Desktop/{}.ipa'.format(sTargetIpaName)
	if len(sAppPath) > 0:
		sShellXcrun += ' {}'.format(sAppPath)
	if len(sTargetIpaName) > 0:
		sShellXcrun += '  -o {}'.format(sOutPutFile)
	result = os.system(sShellXcrun)
	if 0 != result:
		print "Pack failed"

	###scp to ios.dev.anjuke.com
	sDirName = AppManager().getPublishPathByAppName(sAppName)
	sShellScp = 'scp {} mobile@192.168.201.214:{}'.format(sOutPutFile,sDirName)
	result = os.system(sShellScp)

	if 0 != result:
		print "Scp failed"