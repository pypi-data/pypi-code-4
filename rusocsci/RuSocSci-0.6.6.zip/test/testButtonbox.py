#!/usr/bin/env python
## Setup Section
from __future__ import print_function
import logging, time, sys
logging.getLogger().setLevel(logging.DEBUG)
#from psychopy import core, visual, event
from rusocsci import buttonbox

#win = visual.Window([400,300], monitor="testMonitor")
led = [False]*8

## Experiment Section
bb = buttonbox.Buttonbox()
while True:
	buttons = bb.getButtons()
	if len(buttons):
		for c in buttons:
			if ord(c) >= ord('a') and ord(c) < ord('a')+8:
				led[ord(c) - ord('a')] = False
			elif ord(c) >= ord('A') and ord(c) < ord('A')+8:
				led[ord(c) - ord('A')] = True
		bb.setLeds(led)
		print("buttons ({:3d}): {}{}".format(len(buttons), buttons, " "*50), end="\n")
		sys.stdout.flush()

## Cleanup Section
#core.quit()
