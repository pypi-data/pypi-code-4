#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,re

def easySys(sCommand):
	resultTmp = os.popen(sCommand).read()
	result = re.sub(r'[\r\n]','',resultTmp)
	return result