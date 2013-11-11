#!/usr/bin/env python
#from psychopy import core, visual, event
from __future__ import print_function
from rusocsci import joystick, utils
import logging, time, sys, serial


## Setup Section
logging.getLogger().setLevel(logging.DEBUG)
#win = visual.Window([400,300], monitor="testMonitor")
ports = utils.serialList()
i = 0
for port in ports:
	[device, string] = utils.open(port=port)
	print("{:2d} {}".format(i, string))
	i += 1
