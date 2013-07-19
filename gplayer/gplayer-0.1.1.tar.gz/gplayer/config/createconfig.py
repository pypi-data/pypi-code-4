#!/usr/bin/python
# -*- coding: utf-8 -*-

import pkg_resources
import os, sys
import tarfile

FILE="configarchive.tar.gz"
FILE_EXISTS_MSG="The Config-Dir already exists! Overide existing files?"

def showMsg(msg):
	import platform
	if platform.system() == 'Windows':
		import win32ui
		import win32con
		win32ui.MessageBox(msgLines, "Error", win32con.MB_OKCANCEL)
		if result == win32con.MB_IDOK: return True
	else :
		import tkMessageBox
		import Tkinter
		window = Tkinter.Tk()
		window.wm_withdraw()
		answer = tkMessageBox.askokcancel("Warning", msg)
		return answer
	return False

is_pkg = pkg_resources.resource_exists("gplayer.config", FILE)
print("does the resource exist? %s " % (is_pkg))

if is_pkg :
	res = pkg_resources.resource_stream("gplayer.config", FILE)
else :
	print("Konnte Archiv %s nicht in den Ressourcen finden" % (FILE))
	sys.exit(1)
try : tar = tarfile.open(mode='r|gz', fileobj=res)
except : 
	print("Konnte Archiv %s nicht oeffnen" % (FILE))
	sys.exit(1)
# tar.list()

root_dir =  os.path.expanduser(os.path.join('~', '.gPlayer'))
is_dir = os.path.isdir(root_dir)
print("does the config-dir exist? %s " % (is_dir))
doit = True
if is_dir :
	doit = showMsg(FILE_EXISTS_MSG)

if doit: tar.extractall(path=root_dir)


