#!/usr/bin/env python
#from psychopy import core, visual, event
from __future__ import print_function
from rusocsci import joystick, utils
import logging, time, sys

## Setup Section
logging.getLogger().setLevel(logging.DEBUG)
#win = visual.Window([400,300], monitor="testMonitor")
print("list: {}".format(utils.serialList()))
j = joystick.Joystick(port = "COM3")

## Experiment Section
while True:
	print("x: {:3d}                ".format(j.getX()), end="\r")
	sys.stdout.flush()
	time.sleep(1)
 
## Cleanup Section
#core.quit()
