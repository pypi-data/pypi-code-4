import sys
import random
import math
# import uuid
# import snakes.plugins
# snakes.plugins.load('gv', 'snakes.nets', 'nets')
# snakes.plugins.load('labels', 'snakes.nets', 'nets2')
# from nets import *
# from nets2 import *
import sets
import pydot
import copy

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

class PetriNet(object):

	def __init__(self):
		print "New PN created"
		self.P = sets.Set()
		self.T = sets.Set()
		self.F = sets.Set()

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

class VirtualPetriNet(PetriNet):

	def __init__(self, nome):
		super(VirtualPetriNet, self).__init__()
		print "New VPN created"
		self.VP = sets.Set()
		self.VT = sets.Set()
		self.ID = nome
		self.FITNESS_VALUE = 0

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

		print "Adding new whole transition",a,"->",t,"->",b

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

		

class EvolutionaryPetriNet(object):

	def __init__(self, title=None):
		print "New empty EPN created"
		self.VPNS = []
		self.counter_virtualplaces = 0
		self.counter_virtualtransitions = 0
		self.USE_UNIFORM_PROBABILITY = True
		self.O_PRE = -1
		self.O_POST = -1
		self.Title = title
		self.POP_SIZE = 0

		# ""constants""
		self.USE_ROULETTE   = 1
		self.USE_RANKING    = 2
		self.USE_TOURNAMENT = 3

		self.SEL_TYPE = self.USE_TOURNAMENT
		
		self.TOUR_SIZE = 2


	def setPreOrder(self,n):
		self.O_PRE = n
		print " * Maximum pre-order of transitions:", self.O_PRE
	def setPostOrder(self,n): 
		self.O_POST = n
		print " * Maximum pre-order of transitions:", self.O_POST


	def fetchUniqueTransitionId(self):
		self.counter_virtualtransitions += 1
		return self.counter_virtualtransitions
	def fetchUniquePlaceId(self):
		self.counter_virtualplaces += 1
		return self.counter_virtualplaces

	def requestVirtualTransition(self):
		nvt = VirtualTransition("vt"+str(self.fetchUniqueTransitionId()))
		print "New Virtual Transition requested:", nvt
		return nvt
	def requestVirtualPlace(self):
		nvp = VirtualPlace("vp"+str(self.fetchUniquePlaceId()))		
		print "New Virtual Place requested:", nvp
		return nvp


	def addVPN(self,v):
		self.VPNS.append(v)
		print "VPN '",v,"' added to EPN"


	def getVPNS(self):
		return self.VPNS


	def removeSingletons(self, i, list_places):
		""" 
			If a mutation or crossover removes all arcs from/to a virtual place 
			contained in list_places, remove that place.
		"""		
		for p in list_places:
			# print "Checking arcs to",p
			# print self.getVPNS()[i].getArcsConnectedToNode(p)
			if len(self.getVPNS()[i].getArcsConnectedToNode(p))==0:
				self.getVPNS()[i].getVirtualPlaces.remove(p)


	def randomlyModifyWeights(self, i, t):
		print "Mutation #8", "_"*100
		random_diff   = random.choice([-1,+1])	# == 0 ok? TODO
		p_arc = random.choice( self.getVPNS()[i].getArcsConnectedToNode(t) )
		# p_arc.weight += random_diff
		self.getVPNS()[i].setWeight(p_arc, p_arc.weight + random_diff)
	

	def cleanUpThings(self, t, idx=None):

		if idx!=None:
			self.verifyOrder(idx,t)
			pre  = self.getVPNS()[idx].getPreset(t)
			post = self.getVPNS()[idx].getPostset(t)
			self.removeSingletons(idx,pre)
			self.removeSingletons(idx,post)


	def actuallyMutate(self, v):
		index = 0
		if isinstance(v, VirtualPetriNet):
			index = self.getVPNS().index(v)
		else:
			index = v
		p1, t, p2, existing_triple = self.generateTriple(index)

		# mutation introduces a new transition (p1,t),(t,p2)
		# this could invalidate pre- and post-order conditions
		# moreover, we must identify mutation #8 TODO
		if existing_triple:
			self.randomlyModifyWeights(index,t)		
		else:			
			self.getVPNS()[index].addWholeTransition(p1,t,p2)
		
		self.cleanUpThings(t,idx=index)
		"""
		self.verifyOrder(index,t)
		pre  = self.getVPNS()[index].getPreset(t)
		post = self.getVPNS()[index].getPostset(t)
		self.removeSingletons(index,pre)
		self.removeSingletons(index,post)
		"""



	def mutate(self, v):
		"""
			Mutate an arbitrary VPN "v". This method mimickes a C++ overload.
			Returns the preset and postset modified by mutation.
		"""
		if isinstance(v, int):
			if len(self.getVPNS())-1<v:
				print "ERROR: VPN",v,"does not exist!"
				exit(-2)
		if isinstance(v, VirtualPetriNet):
			if v not in self.getVPNS():
				print "ERRO: VPN",v,"does not exist!"
				exit(-2)
		self.actuallyMutate(v)
		
	def verifyPreorder(self,i,t):
		if self.O_PRE == -1: return

		while(True):
			total = 0
			preset = self.getVPNS()[i].getPreset(t)
			for p in preset:
				total += self.getVPNS()[i].getWeight( Arc(p,t) )
			if total <= self.O_PRE:
				return
			else:
				print "Fixing pre-order of transition",t," (",total,")"

			picked_arc = Arc(random.choice(list(preset)),t)
			pa = self.getVPNS()[i].getArc(picked_arc)
			w = pa.weight
			self.getVPNS()[i].setWeight( pa , w-1 ) 
			"""print picked_arc
			w = self.getVPNS()[i].getWeight( picked_arc )	
			self.getVPNS()[i].setWeight( picked_arc , w-1 ) 
			"""

			if self.getVPNS()[i].getArcsConnectedToNode(picked_arc.start) == []:
				print "Singleton detected: removing", picked_arc.start
				# TODO: check whether it is virtual or not
				try:
					self.getVPNS()[i].VP.remove(picked_arc.start)
				except:
					pass


	def verifyPreorderOld(self,i,t):
		if self.O_PRE == -1: return			
		while(True):
			total = 0
			preset = self.getVPNS()[i].getPreset(t)	
			for p in preset:
				total += self.getVPNS()[i].getWeight( Arc(p,t) )
			if total<=self.O_PRE:				
				return
			else:
				print "Fixing pre-order (",total,")"
			total_arcs = len( preset )
			picked_arc = random.randint(0, total_arcs)
			for n,a in enumerate(preset):
				if n==picked_arc:
					break
			w = self.getVPNS()[i].getWeight( Arc(a,t) )
			self.getVPNS()[i].setWeight( Arc(a,t) , w-1 ) 
			if self.getVPNS()[i].getArcsConnectedToNode(a) == []:
				print "Singleton detected: removing", a
				# TODO: check whether it is virtual or not
				self.getVPNS()[i].VP.remove(a)


	def verifyPostorder(self,i,t):
		if self.O_POST == -1: return			
		while(True):
			total = 0
			postset = self.getVPNS()[i].getPostset(t)	
			for p in postset:
				total += self.getVPNS()[i].getWeight( Arc(t,p) )
			if total<=self.O_POST:				
				return
			else:
				print "Fixing post-order (",total,")"
			total_arcs = len( postset )
			picked_arc = random.randint(0, total_arcs)
			for n,a in enumerate(postset):
				if n==picked_arc:
					break
			w = self.getVPNS()[i].getWeight( Arc(t,a) )
			self.getVPNS()[i].setWeight( Arc(t,a) , w-1 ) 
			if self.getVPNS()[i].getArcsConnectedToNode(a) == []:
				print "Singleton detected: removing"
				# TODO: check whether it is virtual or not
				self.getVPNS()[i].VP.remove(a)


	def verifyOrder(self,i,t):
		self.verifyPreorder(i,t)
		self.verifyPostorder(i,t)
		

	def prob_distribution_newplace(self, i):		
		tp = len(self.getVPNS()[i].getAllPlaces())		
		if self.USE_UNIFORM_PROBABILITY:
			ptb = 1./(tp+1)			
		else:
			pass 	# TODO
		return ptb


	def generateTriple(self, i):
		"""
			This methods generates a 3-ple for the mutation, according to the probability distributions 
			defined by programmer (default = uniform).
			It exploits existing places and virtual places from i-th VPN and P^\infty.
			It exploits existing transitions and virtual transitions from i-th VPN and T^\infty.
		"""

		new_p1 = False
		new_p2 = False

		total_places = len(self.getVPNS()[i].getAllPlaces())
		total_prob = total_places +1
		choice = random.uniform(0,total_prob)
		choice_index = int(choice)
		if choice_index>=total_places:
			p1 = self.requestVirtualPlace()
			new_p1 = True
			
		else:
			p1 = list(self.getVPNS()[i].getAllPlaces())[choice_index]
		print "P1 = ", p1

		# le transizioni che vengono toccate sono SOLO quelle virtuali!
		total_transitions = len(self.getVPNS()[i].getVirtualTransitions())
		total_prob = total_transitions +1
		choice = random.uniform(0,total_prob)
		choice_index = int(choice)
		if choice_index>=total_transitions:
			t = self.requestVirtualTransition()
			self.getVPNS()[i].addVirtualTransition(p1)
		else:
			t = list(self.getVPNS()[i].getVirtualTransitions())[choice_index]
		print "T = ", t

		total_places = len(self.getVPNS()[i].getAllPlaces())
		total_prob = total_places +1
		choice = random.uniform(0,total_prob)
		choice_index = int(choice)
		if choice_index>=total_places:
			p2 = self.requestVirtualPlace()
			new_p2 = True
			# self.getVPNS()[i].addVirtualPlace(p1)
		else:
			p2 = list(self.getVPNS()[i].getAllPlaces())[choice_index]
		print "P2 = ", p2

		if new_p1: self.getVPNS()[i].addVirtualPlace(p1)
		if new_p2: self.getVPNS()[i].addVirtualPlace(p2)

		existing_transition = Arc(p1,t) in self.getVPNS()[i].getAllArcs() and  Arc(t,p2) in self.getVPNS()[i].getAllArcs() 
		# first_half = self.getVPNS()[i].getAllArcs().intersection( Arc(p1,t) )
		# second_half = first_half.intersection( Arc(t,p2) ) 

		return p1,t,p2, existing_transition


	def dumpToFile(self, path):

		graph = pydot.Dot(self.Title, graph_type='digraph') 

		for v in self.VPNS:
			v.subDumpToFile(path, graph)

		graph.write_png(path)		


	def mutateAllVPNS(self):
		print "*"*100
		for v in self.getVPNS():
			print "Mutation individual", v
			E.mutate(v)


	def actualCrossover(self, t1, t2, v1, v2, debug=False):
		print "Exchange", t1, "and", t2

		# step 1: identify p_e and p_b for each transition
		preset1  = v1.getPreset(t1)
		postset1 = v1.getPostset(t1)
		pb1 = random.sample(preset1, 1)[0]
		pe1 = random.sample(postset1, 1)[0]

		print "Pb1:", pb1, "Pe1:", pe1

		preset2  = v2.getPreset(t2)
		postset2 = v2.getPostset(t2)
		pb2 = random.sample(preset2, 1)[0]
		pe2 = random.sample(postset2, 1)[0]

		print "Pb2:", pb2, "Pe2:", pe2

		# step 1: copy P+ (renaming)
		v2.addVirtualTransition( t1 )
		v1.addVirtualTransition( t2 )

		# E.dumpToFile("prova0_trans.png")

		""" COPY SUBSTRUCTURES """
		for p in preset1:
			e = v1.getArc(Arc(p,t1))
			if isinstance(p, VirtualPlace):
				if p != pb1:					
					pnew = copy.deepcopy(p)
					if debug:
						pnew.name = "vp"+str(self.fetchUniquePlaceId()) + "(" + pnew.name + ")"
					else:
						pnew.name = "vp"+str(self.fetchUniquePlaceId()) 
					v2.addVirtualPlace( pnew )
					v2.addArc( From=pnew, To=t1, weight=e.weight )					
				else:										
					v2.addArc( From=pb2, To=t1, weight=e.weight  )		
			else:				
				v2.addArc( From=p, To=t1, weight=e.weight )

		# E.dumpToFile("prova0_trans2.png")

		for p in preset2:
			e = v2.getArc(Arc(p,t2))
			if isinstance(p, VirtualPlace):
				if p != pb2:
					pnew = copy.deepcopy(p)
					if debug:
						pnew.name = "vp"+str(self.fetchUniquePlaceId()) + "(" + pnew.name + ")"
					else:
						pnew.name = "vp"+str(self.fetchUniquePlaceId()) 
					v1.addVirtualPlace( pnew )	
					v1.addArc( pnew, t2, weight=e.weight  )
				else:
					v1.addArc( pb1, t2, weight=e.weight  )
			else:
				v1.addArc( p, t2, weight=e.weight )

		# E.dumpToFile("prova0_trans3.png")

		for p in postset1:
			e = v1.getArc(Arc(t1,p))
			if isinstance(p, VirtualPlace):
				if p != pe1:
					pnew = copy.deepcopy(p)
					if debug:
						pnew.name = "vp"+str(self.fetchUniquePlaceId()) + "(" + pnew.name + ")"
					else:
						pnew.name = "vp"+str(self.fetchUniquePlaceId())
					v2.addVirtualPlace( pnew )
					v2.addArc( t1, pnew, weight=e.weight  )
				else:
					v2.addArc( t1, pe2, weight=e.weight  )					
			else:										
				v2.addArc( t1, p, weight=e.weight )				

		# E.dumpToFile("prova0_trans3.png")

		for p in postset2:
			e = v2.getArc(Arc(t2,p))
			if isinstance(p, VirtualPlace):
				if p != pe2:
					pnew = copy.deepcopy(p)
					if debug:
						pnew.name = "vp"+str(self.fetchUniquePlaceId()) + "(" + pnew.name + ")"
					else:
						pnew.name = "vp"+str(self.fetchUniquePlaceId()) 
					v1.addVirtualPlace( pnew )
					v1.addArc( t2, pnew, weight=e.weight  )
				else:
					v1.addArc( t2, pe1, weight=e.weight  )
			else:
				v1.addArc( t2, p, weight=e.weight )

		# E.dumpToFile("prova0_trans4.png")

		""" FINE: RIPULIAMO LE STRUTTURE """
		v1.safeRemoveVirtualTransition(t1)
		v2.safeRemoveVirtualTransition(t2)



	def crossover(self, v1, v2, debug=False):

		print "X"*100

		# step 1: choose two virtual transitions
		pick_1 = random.sample(v1.getVirtualTransitions(),1)[0]
		pick_2 = random.sample(v2.getVirtualTransitions(),1)[0]
				
		# step 2: exchange substructures
		self.actualCrossover(pick_1, pick_2, v1, v2, debug=debug)


	def selection(self):
		if self.SEL_TYPE == self.USE_TOURNAMENT:
			self.tournament()
		elif self.SEL_TYPE == self.USE_RANKING:
			self.ranking()
		else:
			self.roulette()


	def tournament(self):

		selected_population = []

		# for each individual
		for i in range(self.POP_SIZE):

			sampled = random.sample(range(0,self.POP_SIZE), self.TOUR_SIZE)	

			print sampled
			
			best = 0
			best_fitness = self.VPNS[0]
			for s in sampled:
				if self.VPNS[s].FITNESS_VALUE < best_fitness:
					best_fitness = self.VPNS[s].FITNESS_VALUE
					best = s

			selected_population.append( self.VPNS[best] )



	def ranking(self):
		pass
	def roulette(self):
		pass


	def setPopulationSize(self, s):
		if self.MODEL == None:
			print "ERROR: please specify a model before initializing the population"
			exit(-4)
		self.POP_SIZE = s
		print " * Population size set to", self.POP_SIZE
		self.createPopulation()

	def createPopulation(self):
		if self.POP_SIZE == 0:
			print "ERROR: please specify the population's size"
			exit(-5)
		for i in range(self.POP_SIZE):
			# p = VirtualPetriNet("V"+str(i))
			p = copy.deepcopy(self.MODEL)
			p.ID = "V"+str(i)
			self.addVPN(p)
		print " *", self.POP_SIZE, "VPNs added to EPN"



	def useTournament(self, size=2):
		self.SEL_TYPE = self.USE_TOURNAMENT
		self.TOUR_SIZE = size
		print " * Selection mechanism: tournament with tournament size", size
	def useRanking(self):
		self.SEL_TYPE = self.USE_RANKING
	def useRoulette(self):
		self.SEL_TYPE = self.USE_ROULETTE


	def setStaticModel(self,sm):
		self.MODEL = sm


if __name__ == '__main__':
	
	random.seed(5)

	VM = VirtualPetriNet("model")
	VM.addWholeTransition( Place("input"), Transition("transizione"), Place("output") )

	E = EvolutionaryPetriNet()
	E.setStaticModel(VM)
	E.setPopulationSize(10)
	E.useTournament(size=2)
	E.setPreOrder(2)

	"""
	p0 = VirtualPetriNet("V0")
	p1 = VirtualPetriNet("V1")
	p2 = VirtualPetriNet("V2")
	"""

	"""
	vt0 = E.requestVirtualTransition()
	vp0 = E.requestVirtualPlace()
	vp1 = E.requestVirtualPlace()
	vp2 = E.requestVirtualPlace()
	vp3 = E.requestVirtualPlace()
	vp4 = E.requestVirtualPlace()
	vp5 = E.requestVirtualPlace()

	p1.addWholeTransitionList([vp0], vt0, [vp2, vp3])
	p1.addWholeTransitionList([vp2], Transition("vera"), [vp1,Place("output")])
	p2.addWholeTransitionList([vp4, vp5], VirtualTransition("transizione"), [Place("output")])
	"""

	"""
	vt0 = E.requestVirtualTransition()
	vt1 = E.requestVirtualTransition()
	vp0 = E.requestVirtualPlace()
	vp1 = E.requestVirtualPlace()

	p1.addWholeTransitionList( [vp0], vt0, [Place("output")] )
	p1.addPlace(Place("input"))
	p2.addWholeTransitionList( [Place("input")], vt1, [vp1] )
	p2.addPlace(Place("output"))

	E.addVPN(p1)
	E.addVPN(p2)
	"""

	E.dumpToFile("EPN.png")
	
	"""
	for i in range(1,2):
		print "Iteration",i,"^"*100
		# E.setRandomFitness()
		E.selection()
		E.crossover(p1,p2,debug=False)
		E.dumpToFile("prova"+str(i)+"a.png")
		E.mutateAllVPNS()
		E.dumpToFile("prova"+str(i)+"b.png")
	"""