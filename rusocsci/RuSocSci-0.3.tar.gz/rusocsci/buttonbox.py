#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Additional part for the PsychoPy library
# Copyright (C) 2013 Wilbert van Ham, Radboud University Nijmegen
# Distributed under the terms of the GNU General Public License (GPL) version 3 or newer.
from psychopy import core, visual, monitors, event
import sys, serial, time, os, re, logging, glob
if sys.platform == "win32":
	import _winreg

# our buttonbox has id 0403:6001 fro  its UART IC
# make sure you have the pyusb module installed
# for window you may need this: http://sourceforge.net/apps/trac/libusb-win32/wiki
bb = None # serial interface to buttobnbox, if None, we use the keyboard
def __init__():
	global bb
	fileName = _findUsb()
	if fileName == "":
		logging.info("Buttonbox not found.")
		return
	else:
		logging.info("Buttonbox found at: " + fileName)
		
	try:
		bb = serial.Serial(fileName, baudrate=115200, parity='N', timeout = 0.0)  # open serial port
	except Exception as e:
		logging.info("Could not connect to serial port: \n{}".format(e))
		return
		
	# reset connection (needed for Linux of buttonbox was opened before)
	bb.setDTR(True)
	bb.setDTR(False)
	
		
	# collect byes up to "!\x0d\x0a" that identify the type of buttonbox
	beginTime = time.time()
	bytesRead = ""
	while  len(bytesRead) < 3 or (len(bytesRead) >= 3 and bytesRead[-3:] != "!" + "0d0a".decode("hex")):
		if time.time() > beginTime + 3:
			logging.info("Buttonbox timeout")
			bb = None
			return
		bytes=bb.read()
		bytesRead += bytes
		
	if bb:
		logging.info("Buttonbox idstring ({}): {}".format(len(bytesRead), bytesRead.rstrip()))

def __del__():
	global bb
	if bb:
		bb.close()
	
def _findUsb():
	"Find the serial device that our USB buttonbox is connected to."
	if sys.platform == "win32":
		try:
			# find number of FTDI USB to serial devices attached
			reg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
			key = _winreg.CreateKey(reg, r"SYSTEM\CurrentControlSet\services\FTDIBUS\Enum")
			count = _winreg.QueryValueEx(key, "Count")[0]
		except Exception as e:
			logging.info("Could not find USB Buttonbox, no FTDI bus.\n")
			return ""
		
		if count == 0:
			logging.info("No USB Buttonbox connected.")
			return ""
		if count > 1:
			logging.warning("Multiple USB Buttonboxes connected, using the last connected.")
		value = _winreg.QueryValueEx(key, str(count-1))[0]
		logging.info("USB Buttonbox connected with value: "+ value)
		id = value[-4:]
		
		# find port, the following line gives an error in windiows without administrative priviliges
		key = _winreg.CreateKey(reg, r"SYSTEM\CurrentControlSet\Enum\FTDIBUS\VID_0403+PID_6001+A600"+id+r"A\0000\Device Parameters")
		try:
			value = _winreg.QueryValueEx(key, "PortName")[0]
			return value
		except Exception as e:
			logging.info("Could not find USB Buttonbox, no value for PortName: \n", e)
		return ""
	elif sys.platform == "darwin":
		s = os.popen('ls -t /dev/tty.usbserial*').read().rstrip()
		m = s.split()
		if len(m)==0:
			logging.info("Could not find USB Buttonbox. Install the FTDI VCP driver and insert the buttonbox.")
			return ""
		if len(m) > 1:
			logging.info("Multiple USB Buttonboxes connected, using the last connected.")
		serial = m[0] # newest
		logging.info("USB Buttonbox serial interface: "+serial)
		return serial
	else:
		# http://stackoverflow.com/questions/2530096/how-to-find-all-serial-devices-ttys-ttyusb-on-linux-without-opening-them
		# /sys/bus/usb/devices/
		# /sys/devices/pci0000:00/0000:00:1d.0/usb2/2-1/2-1.6/serial
		#s = os.popen('lsusb -d 0403:6001').read().rstrip()
		#if s: # there is a usb device which appears to be our buttonbox
			#now find the corresponding serial device
			#logging.info("USB Buttonbox device found.")
		
		s = os.popen('ls -t /dev/serial/by-id/*FTDI*').read()
		m = s.split()
		if len(m)==0:
			logging.info("Could not find USB Buttonbox")
			#logging.warning("Could not match FTDI device")
			return ""
		if len(m) > 1:
			logging.info("Multiple USB Buttonboxes connected, using the last connected.")
		serial = m[0] # newest
		logging.info("USB Buttonbox serial interface: "+serial)
		return serial
		#else:
		#	logging.info("Could not find USB Buttonbox")
		#	return ""
			
def clearEvents():
	if bb == None:
		event.flushInput(keyboard)
	else:
		bb.flushInput()
	
def getButtons(buttonList=None):
	"""Returns a list of buttons that were pressed on the buttonbox. Falls back to 
	keyboard if there is no buttonbox.

	:Parameters:
		keyList : **None** or []
			Allows the user to specify a set of buttons to check for.
			Only keypresses from this set of keys will be removed from the keyboard buffer.
			If the keyList is None all keys will be checked and the key buffer will be cleared
			completely. NB, pygame doesn't return timestamps (they are always 0)
		There is no timestamp in our buttonbox. Use buttonbox.waitkeys if you want timestamps.

	:Author:
		- 2013 written by Wilbert van Ham
	"""
	global bb
	if bb == None:
		return event.getKeys(keyList=[b.lower() for b in buttonList])
	bb.timeout = 0
	cList = bb.read(1024)
	cListSelected = []
	for c in cList:
		if c in buttonList:
			cListSelected.append(c)
	return cListSelected
			
def waitButtons(maxWait=float("inf"), buttonList=None, timeStamped=False):
	"""
	Same as `~socsci.buttonbox.getButtons`, but halts everything (including drawing) while awaiting
	input from buttonbox. Implicitly clears buttonbox, so any preceding buttonpresses will be lost.

	:Parameters:
		maxWait : any numeric value.
			Maximum number of seconds period and which buttons to wait for. 
			Default is float('inf') which simply waits forever.
		buttonList:
			List of one character strings containing the buttons to react to.
			All other button presses will be ignored. Notethat for BITSI 
			buttonboxes the buttons are identified by capital letters upon press
			and by lower case letters upon release.

	Returns None if times out.
	"""

	global bb
	if bb == None:
		return event.waitKeys(maxWait=maxWait, keyList=[b.lower() for b in buttonList], timeStamped=timeStamped)
	bb.flushInput()
	t = time.time()
	while maxWait - (time.time() - t) > 0:
		bb.timeout = maxWait - (time.time() - t)
		c = bb.read(1)
		if buttonList==None or c in buttonList:
			# return
			break
		else:
			# discard
			c = None
	if hasattr(timeStamped, 'timeAtLastReset'):
		return [(c, time.time() - timeStamped.timeAtLastReset)]
	elif timeStamped:
		# return as a one item list to mimic getButtons behaviour
		return [(c, time.time() - t)]
	else:
		return c
		
# following line ensure that we see all the debugging and info output from the buttonbox
logging.getLogger().setLevel(logging.DEBUG)
__init__()

