#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RuSocSci module for utilities, like listing USB to serial devices and connecting to them.

# Copyright (C) 2013 Wilbert van Ham, Radboud University Nijmegen
# Distributed under the terms of the GNU General Public License (GPL) version 3 or newer.

Known issues:
    - All usb2serial devices are detected. The list of joysticks therefore also contains
      buttonboxes.

Typical usage::

    from psychopy import visual
    from rusocsci import joystick
    import time

    win = visual.Window([400,400])

    nJoys = joystick.getNumJoysticks()#to check if we have any
    id=0
    joy = joystick.Joystick(id)#id must be <= nJoys-1

    while True:#while presenting stimuli
        joy.getX()
        time.sleep(1)
"""
import sys, serial, time, os, re, logging, struct
if sys.platform == "win32":
	import _winreg

# our buttonboxand joystick have id 0403:6001 from its UART IC
# make sure you have the pyusb module installed
# for MS Windows you may need this: http://sourceforge.net/apps/trac/libusb-win32/wiki
def serialList():
	"Get a list of USB to serial devices connected."
	if sys.platform == "win32":
		try:
			# find number of FTDI USB to serial devices attached
			reg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
			key = _winreg.CreateKeyEx(reg, r"SYSTEM\CurrentControlSet\services\FTDIBUS\Enum", 0, _winreg.KEY_READ)
			count = _winreg.QueryValueEx(key, "Count")[0]
		except Exception as e:
			logging.error("Could not find USB joystick, no FTDI bus, \n{}".format(e))
			return ""
		
		if count == 0:
			logging.error("No USB joystick connected.")
			return []
		if count > 1:
			logging.debug("Multiple USB serial connected, last connected is first in list.")
			
		devices = []
		for i in range(count-1, -1, -1):
			value = _winreg.QueryValueEx(key, str(i))[0]
			devices.append(value)
		logging.debug("USB to serial devices: {}".format(devices))
		
		ports = []
		for device in devices:
			id = device[-8:] #for instance 
			# find port, the following line gives an error in windows without administrative priviliges
			key = _winreg.CreateKey(reg, r"SYSTEM\CurrentControlSet\Enum\FTDIBUS\VID_0403+PID_6001+"+id+r"A\0000\Device Parameters")
			try:
				value = _winreg.QueryValueEx(key, "PortName")[0]
				ports.append(value)
			except Exception as e:
				logging.info("Could not find USB serial device, no value for PortName: {}\n".format(e))
		logging.debug("USB to serial interfaces: {}".format(ports))
		return ports
	elif sys.platform == "darwin":
		s = os.popen('ls -t /dev/tty.usbserial*').read().rstrip()
		ports = s.split()
		if len(ports)==0:
			logging.info("Could not find USB serial device. Install the FTDI VCP driver and plug in the device.")
		if len(ports) > 1:
			logging.debug("Multiple USB serial devices connected, last connected is first in list.")
		logging.debug("USB to serial interfaces: {}".format(ports))
		return ports
	else:
		# http://stackoverflow.com/questions/2530096/how-to-find-all-serial-devices-ttys-ttyusb-on-linux-without-opening-them
		# /sys/bus/usb/devices/
		# /sys/devices/pci0000:00/0000:00:1d.0/usb2/2-1/2-1.6/serial
		#s = os.popen('lsusb -d 0403:6001').read().rstrip()
		s = os.popen('ls -t /dev/serial/by-id/*FTDI*').read()
		ports = s.split()
		if len(ports)==0:
			logging.info("Could not find USB serial device.")
		if len(ports) > 1:
			logging.debug("Multiple USB serial devices connected, last connected is first in list.")
		logging.debug("USB to serial interfaces: {}".format(ports))
		return ports


def open(id=0, port=None):
	""" id is position in list (0 is latest), port is 'COM1', /dev/tty, 0 or something similar
	Note that port can also be a real serial port (non USB).
	returns serial connection and id string. """
	device = None
	if port == None:
		ports = serialList()
		if len(ports)>id:
			port = ports[id]
		else:
			logging.error("id {} invalid, number of USB to serial ports found: {}".format(id, len(ports)))
			return [None, ""]
	if port == None or port == "":
		logging.error("No USB to serial port found not found.")
		return [None, ""]
	else:
		logging.debug("Connecting to USB to serial port: {}".format(port))
		
	try:
		device = serial.Serial(port, baudrate=115200, parity='N', timeout = 0.0)  # open serial port
	except Exception as e:
		logging.error("Could not connect to serial port {}: \n{}".format(port, e))
		return None
		
	# reset connection (needed for Linux if port was opened before)
	device.setDTR(True)
	device.setDTR(False)
	
	#idString = "joystick streaming angle, Ready!" + "0d0a".decode("hex")
	# collect byes up to "!\x0d\x0a" that identify the type of device
	beginTime = time.time()
	bytesRead = ""
	while len(bytesRead) < 3 or bytesRead[-3:] != "!\x0d\x0a":
		if time.time() > beginTime + 3:
			logging.error("USB to serial timeout")
			device = None
			return [None, "USB to serial timeout"]
		bytes = device.read()
		#if len(bytes) > 0:
			#print("bytes: #{}#".format(bytes))
		#if len(bytesRead) > 2:
			#print("bytesRead: #{}#".format(bytesRead[-3:]))
		bytesRead += bytes
		
	return [device, bytesRead[:-2]]


