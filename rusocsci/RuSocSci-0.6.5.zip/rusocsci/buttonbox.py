#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RuSocSci module for the BITSI buttonbox

Copyright (C) 2013 Wilbert van Ham, Radboud University Nijmegen
Distributed under the terms of the GNU General Public License (GPL) version 3 or newer.
"""
from psychopy import core, visual, monitors, event
import sys, serial, time, os, re, logging, glob
import utils

# our buttonbox has id 0403:6001 fro  its UART IC
# todo: add support for 2341:0001 (Arduino Uno)
# make sure you have the pyusb module installed
# for window you may need this: http://sourceforge.net/apps/trac/libusb-win32/wiki

class Buttonbox():
	def __init__(self, id=0, port=None):
		[self._device, idString] = utils.open(id, port)
		if idString == "BITSI mode, Ready!" or idString == "BITSI event mode, Ready!":
			logging.debug("Device is a BITSI buttonbox ({}): {}".format(len(idString), idString))
		else:
			logging.error("Device is NOT a BITSI buttonbox ({}): {}".format(len(idString), idString))

	def __del__(self):
		if self._device:
			self._device.close()
				
	def clearEvents(self):
		if self._device == None:
			event.flushInput(keyboard)
		else:
			self._device.flushInput()
		
	def getButtons(self, buttonList=None):
		"""Returns a list of buttons that were pressed on the buttonbox. Falls back to 
		keyboard if there is no buttonbox.

		:Parameters:
		keyList : **None** or []
		Allows the user to specify a set of buttons to check for.
		Only keypresses from this set of keys will be removed from the keyboard buffer.
		If the keyList is None all keys will be checked and the key buffer will be cleared
		completely. NB, pygame doesn't return timestamps (they are always 0)
		here is no timestamp in our buttonbox. Use buttonbox.waitkeys if you want timestamps.

		:Author:
			- 2013 written by Wilbert van Ham
		"""
		if self._device == None:
			try:
				return event.getKeys(keyList=[b.lower() for b in buttonList])
			except:
				raise Exception("No buttonbox connected and no psychopy.event imported for fallback")
		self._device.timeout = 0
		cList = self._device.read(1024)
		#if len(cList)>0:
			#logging.debug("read {} bytes: {}".format(len(cList), cList))
		cListSelected = []
		for c in cList:
			if buttonList==None or c in buttonList:
				cListSelected.append(c)
		return cListSelected
				
	def waitButtons(self, maxWait=float("inf"), buttonList=None, timeStamped=False):
		"""
		Same as getButtons(), but halts everything (including drawing) while awaiting
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
		if self._device == None:
			try:
				return event.waitKeys(maxWait=maxWait, keyList=[b.lower() for b in buttonList], timeStamped=timeStamped)
			except:
				raise Exception("No buttonbox connected and no psychopy.event imported for fallback")
				
		self._device.flushInput()
		t = time.time()
		while maxWait - (time.time() - t) > 0:
			if maxWait == float("inf"):
				self._device.timeout = None
			else:
				self._device.timeout = maxWait - (time.time() - t)
			c = self._device.read(1)
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
			
	def sendMarker(self, leds=[False,False,False,False,False,False,False,False], val=None):
		"""Same as setLeds()"""
		setLeds(self, leds, val)
	def setLeds(self, leds=[False,False,False,False,False,False,False,False], val=None):
		"""Set buttonbox LEDs to a certain pattern """
		if self._device == None:
			raise Exception("No buttonbox connected")
		if val == None:
			val = 0
			for i in range(8):
				if len(leds)>i:
					if leds[i]:
						val += 1<<i
				else:
					break
		self._device.write(chr(val))
		
	def waitLeds(self, leds=[False,False,False,False,False,False,False,False], wait=1.0, val=None):
		"""Set buttonbox LEDs to a certain pattern and wait a while. Reset afterwards."""	
		if self._device == None:
			raise Exception("No buttonbox connected")
		self.setLeds(leds, val)
		time.sleep(wait)
		self.setLeds()

