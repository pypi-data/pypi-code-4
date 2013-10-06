class Node():
	def __init__(self, name):
		self.name = name
	def __str__(self):
			return self.name
	def __cmp__(self,other):
		return self.__hash__() != other.__hash__()
	def __repr__(self):
		return self.name

class Place(Node):
	tokens = 0
	def __repr__(self):
		return "*P* "+self.name
	def __hash__(self):
		return hash("place"+self.name)

class Transition(Node):
	def __repr__(self):
		return "*T* "+self.name
	def __hash__(self):
		return hash("transition"+self.name)

class VirtualPlace(Node):
	tokens = 0
	def __repr__(self):
		return "*VP* "+str(self.name)
	def __hash__(self):
		return hash("virtualplace"+self.name)

class VirtualTransition(Node):
	def __repr__(self):
		return "*VT* "+str(self.name)
	def __hash__(self):
		return hash("virtualtransition"+self.name)

class Arc():
	def __init__(self,a,b):
		self.weight = 1 # default
		self.start = a 
		self.end   = b
	def increment(self):
		self.weight += 1
	def decrement(self):
		self.weight -= 1
	def changeWeight(self,v):
		self.weight += v
	def __repr__(self):
		return "*ARC* ("+str(self.start)+","+str(self.end)+")"
	def __hash__(self):
		return hash("arco"+str(self.start)+str(self.end))
	def __cmp__(self,other):
		return self.__hash__() != other.__hash__()
