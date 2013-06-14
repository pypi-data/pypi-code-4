#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,re

APPNAME_XINFANG = 'i-xinfang'
APPNAME_XINFANG_PAD = 'p-xinfang'
APPNAME_ANJUKE = 'i-anjuke'
APPNAME_ANJUKE_PAD = 'p-anjuke'
APPNAME_HAOZU = 'i-haozu2.0'
APPNAME_HAOZU_PAD = 'p-haozu'
APPNAME_JINPU = 'i-jinpu'
APPNAME_BROKER = 'i-broker'

map_resp_appname = {
	'aifang':APPNAME_XINFANG,
	'xinfangPad':APPNAME_XINFANG_PAD,
	'Anjuke2':APPNAME_ANJUKE,
	'anjukePad':APPNAME_ANJUKE_PAD,
	'Haozu':APPNAME_HAOZU,
	'HaozuPad':APPNAME_HAOZU_PAD,
	'JinPu':APPNAME_JINPU,
	'AnjukeBroker':APPNAME_BROKER
}

basePath = '/var/www/apps/{}/ipa/'
map_appname_path = {
	APPNAME_XINFANG : basePath.format('newhouse'),
	APPNAME_XINFANG_PAD : basePath.format('xinfangPad'),
	APPNAME_ANJUKE : basePath.format('anjuke'),
	APPNAME_ANJUKE_PAD : basePath.format('anjukePad'),
	APPNAME_HAOZU : basePath.format('haozu'),
	APPNAME_HAOZU_PAD : basePath.format('haozuPad'),
	APPNAME_JINPU : basePath.format('JinPu'),
	APPNAME_BROKER : basePath.format('AnjukeBrokerEnterprise')
}