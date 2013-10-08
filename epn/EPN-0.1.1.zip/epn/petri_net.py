from basic import *

class PetriNet(object):

	def __init__(self):
		print "New PN created"
		self.P = set()
		self.T = set()
		self.F = set()

	def getPlaces(self):
		return self.P
	def getArc(self, a):
		for e in self.F:
			if e == a:
				return e 
		return None
	def getArcs(self):
		return self.F
	def getTransitions(self):
		return self.T

	def getWeight(self,a):
		if a in self.F:
			return a.weight
		else:
			print "Arc not found"
			return 0
	def setWeight(self,a,w):
		if w==0:
			print "Weight is zero, removing arc", a
			self.F.remove(a)

			# the removal of an arc may leave an bad-formed transition, i.e.,
			# a transition whose pre- or post-set is empty.

			# TRANSIZIONE -> POSTO
			if self.isTransition(a.start):
				if len(self.getPreset(a.start)) == 0 or len(self.getPostset(a.start)) == 0:
					self.safeRemoveVirtualTransition(a.start)	
				if len(self.getArcsConnectedToNode(a.end)) == 0:
					self.safeRemoveVirtualPlace(a.end)

			# POSTO -> TRANSIZIONE 
			else:
				# elimino la transizione (dovrei controllare se ha altri posti attaccati... TODO)
				if len(self.getPreset(a.end)) == 0 or len(self.getPostset(a.end)) == 0:
					self.safeRemoveVirtualTransition(a.end)	

				# elimino il posto di partenza
				if len(self.getArcsConnectedToNode(a.start)) == 0:
					self.safeRemoveVirtualPlace(a.start)

			# self.removeSingletons()

			"""
			if isinstance(a.start, Transition) or isinstance(a.start, VirtualTransition):
				if self.getPreset(a.start) == []:
					self.safeRemoveVirtualTransition(a.start)	
			elif isinstance(a.end, Transition) or isinstance(a.end, VirtualTransition):
				if self.getPostset(a.end) == []:
					self.safeRemoveVirtualTransition(a.end)	
			"""

			"""
			if isinstance(a.start, Place) or isinstance(a.start, VirtualPlace):
				self.safeRemoveVirtualTransition(a.end)
			if isinstance(a.end, Place) or isinstance(a.end, VirtualPlace):
				self.safeRemoveVirtualTransition(a.end)
			"""

			"""
			print "K"*100
			print a
			print self.getArcsConnectedToNode(a.start)
			print self.getArcsConnectedToNode(a.end)
		
			# check consistency
			try:
				if self.getArcsConnectedToNode(a.start) == []:
					self.safeRemoveVirtualTransition(a.start)
				if self.getArcsConnectedToNode(a.end) == []:
					self.safeRemoveVirtualTransition(a.end)
			except:
				pass
			"""

			return
		if a in self.F:
			print "Old weight:", a.weight
			a.weight = w
			print "New weight:", a.weight
		else:
			print "ERROR: Arc not found"	

	def getArcsConnectedToNode(self,p):
		list_places = []
		for a in self.F:
			if a.start == p or a.end == p:
				list_places.append(a)
		return list_places


	def addPlace(self,p):		
		if isinstance(p, Place):
			self.P.add(p)
			print "Place",p,"added"
		return len(self.P)
	def addTransition(self,t):
		if isinstance(t, Transition):
			self.T.add(t)
			print "Transition",t,"added"
			return len(self.T)
	
	def addArc(self,From=None,To=None,arc=None,weight=1):
		if arc!=None:
			From = arc.start
			To   = arc.end

		if (self.isPlace(From)) and (self.isTransition(To)):			
			# print "Adding input place '", From,"' to transition '",To,"'"
			a = Arc(From,To)
			a.weight = weight
			self.F.add( a )
			return
		if (self.isTransition(From)) and (self.isPlace(To)):
			# print "Adding output place '",To,"' to transition '",From,"'"
			a = Arc(From,To)
			a.weight = weight
			self.F.add( a )
			return

	def removeArc(self, a):
		print "Arc",a,"removed"
		self.F.remove(a)

	def addCompleteTransition(self,p1, t, p2):		
		self.addArc( arc=Arc(p1,t) )
		self.addArc( arc=Arc(t,p2) )
		print "Complete transition",p1,"->",t,"->",p2,"added"
		return self.F