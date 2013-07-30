from actor import *
from runtime import *
# ObjTopState
#  - ObjErrorState
#  - ObjLeftState
#     - ObjLeftChildState *
#     - ObjLeftChildState2 *
#  - ObjRightState *
#     - ObjRightChildState *
#
class ObjTopState(ActorTopState):
	
	def __init__(self, ctx):
		self._ctx = ctx 

	def onFatalError(self):
		print "FatalError"
		self.transition(ObjErrorState)

class ObjErrorState(ObjTopState):

	def _enter(self):
		print "entered Error State"

@initialState
class ObjLeftState(ObjTopState):

	def _enter(self):
		print "Enter Left State"

	def _exit(self):
		print "Exit Left State"

	def onUpdate(self):
		self.transition(ObjRightState)

@initialState
class ObjLeftChildState(ObjLeftState):

	def _enter(self):
		print str(str(self._ctx))
		print "Enter Left Child State"

	def _exit(self):
		print "Exit Left Child State"

	def onUpdate(self):
		self.transition(ObjRightState)
	
class ObjLeftChildState2(ObjLeftState):
	pass	

class ObjRightState(ObjTopState):

	def onUpdate(self):
		self._transition(ObjLeftState)

	def onSample(self):
		print "Sample received"

@initialState
class ObjRightChildState(ObjRightState):

	def onUpdate(self):
		self.transition(ObjLeftState)


obj = ObjTopState({"x":10})
obj.transition(ObjLeftChildState)
obj.transition(ObjLeftChildState2)
obj.transition(ObjTopState)

obj.sendFatalError()
obj.sendFini()

while True:
	msg = GetMessage()
	if not msg:
		break
	DispatchMessage(msg)