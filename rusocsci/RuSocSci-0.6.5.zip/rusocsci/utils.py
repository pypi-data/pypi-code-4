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
	
class HideStderr(object):
	'''A context manager that block stdout for its scope, usage:

	with HideOutput():
		os.system('ls -l')
	'''

	def __init__(self, *args, **kw):
		sys.stderr.flush()
		self._origstderr = sys.stderr
		self._oldstderr_fno = os.dup(sys.stderr.fileno())
		self._devnull = os.open(os.devnull, os.O_WRONLY)

	def __enter__(self):
		self._newstderr = os.dup(2)
		os.dup2(self._devnull, 2)
		os.close(self._devnull)
		sys.stdout = os.fdopen(self._newstderr, 'w')

	def __exit__(self, exc_type, exc_val, exc_tb):
		sys.stderr = self._origstderr
		sys.stderr.flush()
		os.dup2(self._oldstderr_fno, 2)


# our buttonboxand joystick have id 0403:6001 from its UART IC
# make sure you have the pyusb module installed
# for MS Windows you may need this: http://sourceforge.net/apps/trac/libusb-win32/wiki
# FTDIBUS
def _winList(service, bus=None, suffix=None):
	"Helper for windows for serialList function"
	try:
		# find number of FTDI USB to serial devices attached
		reg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
		keyString = r"SYSTEM\CurrentControlSet\services""\\" + service + r"\Enum"
		key = _winreg.CreateKeyEx(reg, keyString, 0, _winreg.KEY_READ)
		count = _winreg.QueryValueEx(key, "Count")[0]
	except Exception as e:
		logging.info("Could not create service key string: {}".format(keyString))
		return []
	
	if count == 0:
		logging.debug("No "+ service +" USB to serial device connected.")
	if count > 1:
		logging.debug("Multiple "+ service +"  USB serial connected, last connected is first in list.")
		
	devices = []
	for i in range(count-1, -1, -1):
		value = _winreg.QueryValueEx(key, str(i))[0]
		devices.append(value)
	logging.debug("USB to serial devices ({}): {}".format(service, devices))
	
	# find the corresponding serial ports
	ports = []
	for device in devices:
		#device is something like: ur"USB\VID_0403&PID_6001\AH01L3OL" or "USB\VID_2341&PID_0043\6493433313535141D0B2"
		id = device[22:]
		# find port, the following line gives an error in windows without administrative priviliges
		try:
			if bus:
				keyString = r"SYSTEM\CurrentControlSet\Enum""\\" + bus + id + suffix + r"\Device Parameters"
			else:
				keyString = r"SYSTEM\CurrentControlSet\Enum""\\" + device + r"\Device Parameters"
			key = _winreg.CreateKey(reg, keyString)
		except Exception as e:
			logging.info("Could not create device key string: {}".format(keyString))
			return []
		try:
			value = _winreg.QueryValueEx(key, "PortName")[0]
			ports.append(value)
		except Exception as e:
			logging.info("Could not find USB serial device, no value for PortName: {}\n".format(e))
	return ports

def serialList():
	"""Get a list of USB to serial devices connected. The returned list is that of the serial ports."""
	if sys.platform == "win32":
		ports = _winList("FTDIBUS", r"FTDIBUS\VID_0403+PID_6001+", r"A\0000") # FTDI based (Arduino 2009)
		ports += _winList("usbser") # ACM based, Arduino Uno, Uno R3, Leonardo
		# usbser should be generic and work for all USB to serial interfaces
		logging.debug("USB to serial ports: {}".format(ports))
		return ports
	elif sys.platform == "darwin":
		# /dev/tty.usbserial* for FTDI (0403:6001) in Arduino 2009
		# /dev/tty.usbmodem* for Arduino Uno R3 (2341:0043)
		# the latter probably works for Arduino Leonardo (2341:8036) as well (todo: test)
		with HideStderr():
			s = os.popen('ls -t /dev/tty.usbserial* /dev/tty.usbmodem*').read().rstrip()
		ports = s.split()
		if len(ports)==0:
			logging.info("Could not find USB serial device. Install the FTDI VCP/Arduino driver and plug in the device.")
		if len(ports) > 1:
			logging.debug("Multiple USB serial devices connected, last connected is first in list.")
		logging.debug("USB to serial interfaces: {}".format(ports))
		return ports
	else:
		# /dev/serial/by-id/*FTDI* for FTDI (0403:6001) in Arduino 2009
		# /dev/ttyACM? for Arduino Uno R3 (2341:0043)
		# the latter probably works for Arduino Leonardo (2341:8036) as well (todo: test)
		with HideStderr():
			s = os.popen('ls -t /dev/serial/by-id/*FTDI* /dev/ttyACM?').read()
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
		
	# reset connection
	device.flushInput()
	# switching the next two lines leads to stray characters prior to the id string on ACM devices
	# leaving out the next two lines leads to the id string not always being sent
	device.setDTR(False) 
	device.setDTR(True)
	
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


