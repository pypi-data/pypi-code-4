from petri_net import *
import pydot

class VirtualPetriNet(PetriNet):

	def __init__(self, nome):
		super(VirtualPetriNet, self).__init__()
		print "New VPN created"
		self.VP = set()
		self.VT = set()
		self.ID = nome
		self.FITNESS_VALUE = 0

	def setID(self,nome):
		self.ID = nome

	def subDumpToFile(self, path, G):
		# graph = pydot.Dot(self.ID, graph_type='digraph') 	

		#@ graph = pydot.Subgraph(self.ID, rank='same') 
		graph = pydot.Subgraph("cluster"+self.ID) 
	
		for p in self.getPlaces():
			graph.add_node(pydot.Node(self.ID+str(p), label=str(p), shape="circle", fixed_size="True", width="1", penwidth="2" )) 
		for p in self.getVirtualPlaces():
			graph.add_node(pydot.Node(self.ID+str(p), label=str(p), shape="circle", fixed_size="True", width="1", color="darkgreen", penwidth="2" )) 

		for t in self.getTransitions():
			graph.add_node(pydot.Node(self.ID+str(t), label=str(t), shape="rectangle", style="filled", fillcolor="grey9", fontcolor="white", width="1"))
		for t in self.getVirtualTransitions():
			graph.add_node(pydot.Node(self.ID+str(t), label=str(t), shape="rectangle", style="filled", fillcolor="lightgrey", fontcolor="black", width="1"))

		for a in self.getAllArcs():
			edge = pydot.Edge( self.ID+str(a.start), self.ID+str(a.end), label=a.weight )
			graph.add_edge(edge)
			pass

		G.add_subgraph(graph) 


	def __repr__(self):
		return self.ID

	def getAllPlaces(self):
		return self.P.union(self.VP)
	def getStaticPlaces(self):
		return self.P
	def getVirtualPlaces(self):
		return self.VP

	def getAllTransitions(self):
		return self.T.union(self.VT)
	def getStaticTransitions(self):
		return self.T
	def getVirtualTransitions(self):
		return self.VT

	def getAllArcs(self):
		return self.F

	def addPlace(self,p):
		if isinstance(p, Place):
			# print p, "is a Place"
			super(VirtualPetriNet, self).addPlace(p)
			return
		if isinstance(p, VirtualPlace):
			# print p, "is a VirtualPlace"
			self.addVirtualPlace(p)
	def addVirtualPlaces(self,pl):
		pl = filter( lambda x: isinstance(x, VirtualPlace), pl )
		for p in pl:
			self.addVirtualPlace(p)

	def safeRemoveVirtualPlace(self,p):
		print "Removing place", p
		if isinstance(p, VirtualPlace):
			print "Okay, it's virtual"
			for a in self.getArcsConnectedToNode(p):
				self.F.remove(a)
				print "Removing pending arc", a
			self.VP.remove(p)
	def safeRemoveVirtualPlaces(self, listp):
		for p in listp:
			self.safeRemoveVirtualPlace(p)


	def safeRemoveVirtualTransition(self,t):
		nodi = []
		for a in self.getArcsConnectedToNode(t):
			inv = None
			if a.start != t:
				inv = a.start
			else:
				inv = a.end
			nodi.append(inv)
			self.F.remove(a)
		self.VT.remove(t)

		# in case of loops, everything blows up: we use try instead.
		for n in nodi:
			if self.getArcsConnectedToNode(n) == []:
				if isinstance(n, VirtualPlace):
					try:
						self.VP.remove(n)
					except:
						pass



	def addVirtualPlace(self,vp):
		if isinstance(vp, VirtualPlace):
			self.VP.add(vp)
			# print "Virtual place '",vp,"' added to", self.ID
			return self.VP

	def addTransition(self,t):
		if isinstance(t, Transition):
			super(VirtualPetriNet, self).addTransition(t)
			return
		if isinstance(t, VirtualTransition):
			self.addVirtualTransition(t)

	def addVirtualTransition(self,vt):
		if isinstance(vt, VirtualTransition):
			self.VT.add(vt)
			# print "Virtual transition '",vt,"' added"
			return self.VT

	def isPlace(self,x):
		return (isinstance(x, Place) or isinstance(x, VirtualPlace))
	def isTransition(self,x):
		return (isinstance(x, Transition) or isinstance(x, VirtualTransition))

	def addArcs(self, arclist):
		for a in arclist:
			self.addArc(arc=a)

	def getPreset(self, a):
		if self.isPlace(a):
			return { arco.start for arco in self.F if arco.end==a }
		if self.isTransition(a):
			return { arco.start for arco in self.F if arco.end==a }

	def getPostset(self, a):
		if self.isPlace(a):
			return { arco.end for arco in self.F if arco.start==a }
		if self.isTransition(a):
			return { arco.end for arco in self.F if arco.start==a }


	def addWholeTransition(self,a,t,b):

		# print "Adding new whole transition",a,"->",t,"->",b

		if a not in self.getAllPlaces():
			self.addPlace(a)
		if b not in self.getAllPlaces():
			self.addPlace(b)
		if t not in self.getAllTransitions():
			self.addTransition(t)

		self.addArc( arc=Arc(a,t) )
		self.addArc( arc=Arc(t,b) )
		
		print "New whole transition '",a,"' -> '",t,"' -> '",b,"' created"		


	def addWholeTransitionList(self,a,t,b):

		combs = [(x,t,y) for x in a for y in b]
		for p1,trans,p2 in combs:
			self.addWholeTransition(p1,trans,p2)

		