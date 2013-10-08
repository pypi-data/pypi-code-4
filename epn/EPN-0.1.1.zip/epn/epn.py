import sys
import random
import math
import sets
import pydot
import copy

class Node(object):
	def __init__(self, name):
		self.name = name
	def __str__(self):
			return self.name
	def __cmp__(self,other):
		return self.__hash__() != other.__hash__()
	def __repr__(self):
		return self.name

class Place(Node):
	def __init__(self, name, tokens=0):
		self.name = name
		self.tokens = tokens
		super(Place, self).__init__(name)	
	def __repr__(self):
		return "*P* "+self.name
	def __hash__(self):
		return hash("place"+self.name)

class Transition(Node):
	def __init__(self, name, parameter=0):
		self.parameter = parameter
		self.name = name
		super(Transition, self).__init__(name)
	def __repr__(self):
		return "*T* "+self.name
	def __hash__(self):
		return hash("transition"+self.name)

class ResizablePlace(Node):
	def __init__(self, name, tokens=0):
		self.name = name
		self.tokens = tokens
		super(Place, self).__init__(name)	
	def __repr__(self):
		return "*RP* "+str(self.name)
	def __hash__(self):
		return hash("Resizableplace"+self.name)

class ResizableTransition(Node):
	def __init__(self, name, parameter=0):
		self.parameter = parameter
		self.name = name
		super(HiddenTransition, self).__init__(name)
	def __repr__(self):
		return "*RT* "+str(self.name)
	def __hash__(self):
		return hash("Resizabletransition"+self.name)

class Arc():
	def __init__(self,a,b):
		self.weight = 1 # default
		self.start = a 
		self.end   = b
	def increment(self):
		self.weight += 1
	def decrement(self):
		self.weight -= 1
	def change_weight(self,v):
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

	def get_places(self):
		return self.P
	def get_arc(self, a):
		for e in self.F:
			if e == a:
				return e 
		return None
	def get_arcs(self):
		return self.F
	def get_transitions(self):
		return self.T

	def get_weight(self,a):
		if a in self.F:
			return a.weight
		else:
			print "Arc not found"
			return 0
	def set_weight(self,a,w):
		if w==0:
			print "Weight is zero, removing arc", a
			self.F.remove(a)

			# the removal of an arc may leave an bad-formed transition, i.e.,
			# a transition whose pre- or post-set_ is empty.

			# TRANSIZIONE -> POSTO
			if self.isTransition(a.start):
				if len(self.get_Preset_(a.start)) == 0 or len(self.get_Postset_(a.start)) == 0:
					self.safeRemoveResizableTransition(a.start)	
				if len(self.get_ArcsConnectedToNode(a.end)) == 0:
					self.safeRemoveResizablePlace(a.end)

			# POSTO -> TRANSIZIONE 
			else:
				# elimino la transizione (dovrei controllare se ha altri posti attaccati... TODO)
				if len(self.get_Preset_(a.end)) == 0 or len(self.get_Postset_(a.end)) == 0:
					self.safeRemoveResizableTransition(a.end)	

				# elimino il posto di partenza
				if len(self.get_ArcsConnectedToNode(a.start)) == 0:
					self.safeRemoveResizablePlace(a.start)

			# self.removeSingletons()

			"""
			if isinstance(a.start, Transition) or isinstance(a.start, ResizableTransition):
				if self.get_Preset_(a.start) == []:
					self.safeRemoveResizableTransition(a.start)	
			elif isinstance(a.end, Transition) or isinstance(a.end, ResizableTransition):
				if self.get_Postset_(a.end) == []:
					self.safeRemoveResizableTransition(a.end)	
			"""

			"""
			if isinstance(a.start, Place) or isinstance(a.start, ResizablePlace):
				self.safeRemoveResizableTransition(a.end)
			if isinstance(a.end, Place) or isinstance(a.end, ResizablePlace):
				self.safeRemoveResizableTransition(a.end)
			"""

			"""
			print "K"*100
			print a
			print self.get_ArcsConnectedToNode(a.start)
			print self.get_ArcsConnectedToNode(a.end)
		
			# check consistency
			try:
				if self.get_ArcsConnectedToNode(a.start) == []:
					self.safeRemoveResizableTransition(a.start)
				if self.get_ArcsConnectedToNode(a.end) == []:
					self.safeRemoveResizableTransition(a.end)
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

	def get_ArcsConnectedToNode(self,p):
		list_places = []
		for a in self.F:
			if a.start == p or a.end == p:
				list_places.append(a)
		return list_places


	def add_place(self,p):		
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

		if (self.is_place(From)) and (self.is_transition(To)):			
			# print "Adding input place '", From,"' to transition '",To,"'"
			a = Arc(From,To)
			a.weight = weight
			self.F.add( a )
			return
		if (self.is_transition(From)) and (self.is_place(To)):
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

class ResizablePetriNet(PetriNet):

	def __init__(self, nome):
		super(ResizablePetriNet, self).__init__()
		print "New RPN created"
		self.RP = sets.Set()
		self.RT = sets.Set()
		self.ID = nome
		self.FITNESS_VALUE = 0

	def get_ID(self):
		return self.ID

	def subDumpToFile(self, path, G):
		# graph = pydot.Dot(self.ID, graph_type='digraph') 	

		#@ graph = pydot.Subgraph(self.ID, rank='same') 
		graph = pydot.Subgraph("cluster"+self.ID) 
	
		for p in self.get_Places():
			graph.add_node(pydot.Node(self.ID+str(p), label=str(p), shape="circle", fixed_size="True", width="1", penwidth="2" )) 
		for p in self.set_resizable_Places():
			graph.add_node(pydot.Node(self.ID+str(p), label=str(p), shape="circle", fixed_size="True", width="1", color="darkgreen", penwidth="2" )) 

		for t in self.get_Transitions():
			graph.add_node(pydot.Node(self.ID+str(t), label=str(t), shape="rectangle", style="filled", fillcolor="grey9", fontcolor="white", width="1"))
		for t in self.set_resizable_Transitions():
			graph.add_node(pydot.Node(self.ID+str(t), label=str(t), shape="rectangle", style="filled", fillcolor="lightgrey", fontcolor="black", width="1"))

		for a in self.set_all_Arcs():
			edge = pydot.Edge( self.ID+str(a.start), self.ID+str(a.end), label=a.weight )
			graph.add_edge(edge)
			pass

		G.add_subgraph(graph) 


	def __repr__(self):
		return self.ID

	def get_all_places(self):
		return self.P.union(self.RP)
	def get_static_places(self):
		return self.P
	def get_resizable_places(self):
		return self.RP

	def get_all_transitions(self):
		return self.T.union(self.RT)
	def get_static_transitions(self):
		return self.T
	def get_hidden_transitions(self):
		return self.RT

	def get_all_arcs(self):
		return self.F


	def add_place(self,p):
		if isinstance(p, Place):
			# print p, "is a Place"
			super(ResizablePetriNet, self).add_place(p)
			return
		if isinstance(p, ResizablePlace):
			# print p, "is a ResizablePlace"
			self.addResizablePlace(p)
	def addResizablePlaces(self,pl):
		pl = filter( lambda x: isinstance(x, ResizablePlace), pl )
		for p in pl:
			self.addResizablePlace(p)

	def safeRemoveResizablePlace(self,p):
		print "Removing place", p
		if isinstance(p, ResizablePlace):
			print "Okay, it's Resizable"
			for a in self.get_ArcsConnectedToNode(p):
				self.F.remove(a)
				print "Removing pending arc", a
			self.RP.remove(p)
	def safeRemoveResizablePlaces(self, listp):
		for p in listp:
			self.safeRemoveResizablePlace(p)


	def safeRemoveResizableTransition(self,t):
		nodi = []
		for a in self.get_ArcsConnectedToNode(t):
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
			if self.get_ArcsConnectedToNode(n) == []:
				if isinstance(n, ResizablePlace):
					try:
						self.RP.remove(n)
					except:
						pass



	def addResizablePlace(self,rp):
		if isinstance(rp, ResizablePlace):
			self.RP.add(rp)
			# print "Resizable place '",rp,"' added to", self.ID
			return self.RP

	def addTransition(self,t):
		if isinstance(t, Transition):
			super(ResizablePetriNet, self).addTransition(t)
			return
		if isinstance(t, ResizableTransition):
			self.addResizableTransition(t)

	def add_resizable_transition(self,vt):
		if isinstance(vt, ResizableTransition):
			self.VT.add(vt)
			# print "Resizable transition '",vt,"' added"
			return self.VT

	def is_place(self,x):
		return (isinstance(x, Place) or isinstance(x, ResizablePlace))
	def is_transition(self,x):
		return (isinstance(x, Transition) or isinstance(x, ResizableTransition))

	def add_arcs(self, arclist):
		for a in arclist:
			self.addArc(arc=a)

	def get_preset(self, a):
		if self.is_place(a):
			return { arco.start for arco in self.F if arco.end==a }
		if self.is_transition(a):
			return { arco.start for arco in self.F if arco.end==a }

	def get_postset(self, a):
		if self.is_place(a):
			return { arco.end for arco in self.F if arco.start==a }
		if self.is_transition(a):
			return { arco.end for arco in self.F if arco.start==a }


	def add_whole_transition(self,a,t,b):

		print "Adding new whole transition",a,"->",t,"->",b

		if a not in self.get_all_places():
			self.add_place(a)
		if b not in self.get_all_places():
			self.add_place(b)
		if t not in self.get_all_transitions():
			self.addTransition(t)

		self.addArc( arc=Arc(a,t) )
		self.addArc( arc=Arc(t,b) )
		
		print "New whole transition '",a,"' -> '",t,"' -> '",b,"' created"		


	def add_whole_transitionList(self,a,t,b):

		combs = [(x,t,y) for x in a for y in b]
		for p1,trans,p2 in combs:
			self.add_whole_transition(p1,trans,p2)

		

class EvolutionaryPetriNet(object):

	def __init__(self, title=None):
		print "New empty EPN created"
		self.RPNS = []
		self.counter_Resizableplaces = 0
		self.counter_Resizabletransitions = 0
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


	def set_pre_order(self,n):
		self.O_PRE = n
		print " * Maximum pre-order of transitions:", self.O_PRE
	def set_post_order(self,n): 
		self.O_POST = n
		print " * Maximum pre-order of transitions:", self.O_POST


	def fetch_unique_transition_ID(self):
		self.counter_Resizabletransitions += 1
		return self.counter_Resizabletransitions
	def fetch_unique_place_ID(self):
		self.counter_Resizableplaces += 1
		return self.counter_Resizableplaces

	def request_resizable_transition(self):
		nvt = ResizableTransition("vt"+str(self.fetchUniqueTransitionId()))
		print "New Resizable Transition requested:", nvt
		return nvt
	def request_resizable_place(self):
		nrp = ResizablePlace("rp"+str(self.fetchUniquePlaceId()))		
		print "New Resizable Place requested:", nrp
		return nrp


	def addRPN(self,v):
		self.RPNS.append(v)
		print "RPN '",v,"' added to EPN"


	def get_RPNS(self):
		return self.RPNS


	def removeSingletons(self, i, list_places):
		""" 
			If a mutation or crossover removes all arcs from/to a Resizable place 
			contained in list_places, remove that place.
		"""		
		for p in list_places:
			# print "Checking arcs to",p
			# print self.get_RPNS()[i].get_ArcsConnectedToNode(p)
			if len(self.get_RPNS()[i].get_ArcsConnectedToNode(p))==0:
				self.get_RPNS()[i].set_resizable_Places.remove(p)


	def randomlyModifyWeights(self, i, t):
		print "Mutation #8", "_"*100
		random_diff   = random.choice([-1,+1])	# == 0 ok? TODO
		p_arc = random.choice( self.get_RPNS()[i].get_ArcsConnectedToNode(t) )
		# p_arc.weight += random_diff
		self.get_RPNS()[i].set_Weight(p_arc, p_arc.weight + random_diff)
	

	def cleanUpThings(self, t, idx=None):

		if idx!=None:
			self.verifyOrder(idx,t)
			pre  = self.get_RPNS()[idx].get_Preset_(t)
			post = self.get_RPNS()[idx].get_Postset_(t)
			self.removeSingletons(idx,pre)
			self.removeSingletons(idx,post)


	def actuallyMutate(self, v):
		index = 0
		if isinstance(v, ResizablePetriNet):
			index = self.get_RPNS().index(v)
		else:
			index = v
		p1, t, p2, existing_triple = self.generateTriple(index)

		# mutation introduces a new transition (p1,t),(t,p2)
		# this could invalidate pre- and post-order conditions
		# moreover, we must identify mutation #8 TODO
		if existing_triple:
			self.randomlyModifyWeights(index,t)		
		else:			
			self.get_RPNS()[index].add_whole_transition(p1,t,p2)
		
		self.cleanUpThings(t,idx=index)
		"""
		self.verifyOrder(index,t)
		pre  = self.get_RPNS()[index].get_Preset_(t)
		post = self.get_RPNS()[index].get_Postset_(t)
		self.removeSingletons(index,pre)
		self.removeSingletons(index,post)
		"""



	def mutate(self, v):
		"""
			Mutate an arbitrary RPN "v". This method mimickes a C++ overload.
			Returns the preset_ and postset_ modified by mutation.
		"""
		if isinstance(v, int):
			if len(self.get_RPNS())-1<v:
				print "ERROR: RPN",v,"does not exist!"
				exit(-2)
		if isinstance(v, ResizablePetriNet):
			if v not in self.get_RPNS():
				print "ERRO: RPN",v,"does not exist!"
				exit(-2)
		self.actuallyMutate(v)
		
	def verifyPreorder(self,i,t):
		if self.O_PRE == -1: return

		while(True):
			total = 0
			preset_ = self.get_RPNS()[i].get_Preset_(t)
			for p in preset_:
				total += self.get_RPNS()[i].get_Weight( Arc(p,t) )
			if total <= self.O_PRE:
				return
			else:
				print "Fixing pre-order of transition",t," (",total,")"

			picked_arc = Arc(random.choice(list(preset_)),t)
			pa = self.get_RPNS()[i].get_Arc(picked_arc)
			w = pa.weight
			self.get_RPNS()[i].set_Weight( pa , w-1 ) 
			"""print picked_arc
			w = self.get_RPNS()[i].get_Weight( picked_arc )	
			self.get_RPNS()[i].set_Weight( picked_arc , w-1 ) 
			"""

			if self.get_RPNS()[i].get_ArcsConnectedToNode(picked_arc.start) == []:
				print "Singleton detected: removing", picked_arc.start
				# TODO: check whether it is Resizable or not
				try:
					self.get_RPNS()[i].RP.remove(picked_arc.start)
				except:
					pass


	def verifyPreorderOld(self,i,t):
		if self.O_PRE == -1: return			
		while(True):
			total = 0
			preset_ = self.get_RPNS()[i].get_Preset_(t)	
			for p in preset_:
				total += self.get_RPNS()[i].get_Weight( Arc(p,t) )
			if total<=self.O_PRE:				
				return
			else:
				print "Fixing pre-order (",total,")"
			total_arcs = len( preset_ )
			picked_arc = random.randint(0, total_arcs)
			for n,a in enumerate(preset_):
				if n==picked_arc:
					break
			w = self.get_RPNS()[i].get_Weight( Arc(a,t) )
			self.get_RPNS()[i].set_Weight( Arc(a,t) , w-1 ) 
			if self.get_RPNS()[i].get_ArcsConnectedToNode(a) == []:
				print "Singleton detected: removing", a
				# TODO: check whether it is Resizable or not
				self.get_RPNS()[i].RP.remove(a)


	def verifyPostorder(self,i,t):
		if self.O_POST == -1: return			
		while(True):
			total = 0
			postset_ = self.get_RPNS()[i].get_Postset_(t)	
			for p in postset_:
				total += self.get_RPNS()[i].get_Weight( Arc(t,p) )
			if total<=self.O_POST:				
				return
			else:
				print "Fixing post-order (",total,")"
			total_arcs = len( postset_ )
			picked_arc = random.randint(0, total_arcs)
			for n,a in enumerate(postset_):
				if n==picked_arc:
					break
			w = self.get_RPNS()[i].get_Weight( Arc(t,a) )
			self.get_RPNS()[i].set_Weight( Arc(t,a) , w-1 ) 
			if self.get_RPNS()[i].get_ArcsConnectedToNode(a) == []:
				print "Singleton detected: removing"
				# TODO: check whether it is Resizable or not
				self.get_RPNS()[i].RP.remove(a)


	def verifyOrder(self,i,t):
		self.verifyPreorder(i,t)
		self.verifyPostorder(i,t)
		

	def prob_distribution_newplace(self, i):		
		tp = len(self.get_RPNS()[i].set_all_places())		
		if self.USE_UNIFORM_PROBABILITY:
			ptb = 1./(tp+1)			
		else:
			pass 	# TODO
		return ptb


	def generateTriple(self, i):
		"""
			This methods generates a 3-ple for the mutation, according to the probability distributions 
			defined by programmer (default = uniform).
			It exploits existing places and Resizable places from i-th RPN and P^\infty.
			It exploits existing transitions and Resizable transitions from i-th RPN and T^\infty.
		"""

		new_p1 = False
		new_p2 = False

		total_places = len(self.get_RPNS()[i].set_all_places())
		total_prob = total_places +1
		choice = random.uniform(0,total_prob)
		choice_index = int(choice)
		if choice_index>=total_places:
			p1 = self.requestResizablePlace()
			new_p1 = True
			
		else:
			p1 = list(self.get_RPNS()[i].set_all_places())[choice_index]
		print "P1 = ", p1

		# le transizioni che vengono toccate sono SOLO quelle Resizablei!
		total_transitions = len(self.get_RPNS()[i].set_resizable_Transitions())
		total_prob = total_transitions +1
		choice = random.uniform(0,total_prob)
		choice_index = int(choice)
		if choice_index>=total_transitions:
			t = self.requestResizableTransition()
			self.get_RPNS()[i].addResizableTransition(p1)
		else:
			t = list(self.get_RPNS()[i].set_resizable_Transitions())[choice_index]
		print "T = ", t

		total_places = len(self.get_RPNS()[i].set_all_places())
		total_prob = total_places +1
		choice = random.uniform(0,total_prob)
		choice_index = int(choice)
		if choice_index>=total_places:
			p2 = self.requestResizablePlace()
			new_p2 = True
			# self.get_RPNS()[i].addResizablePlace(p1)
		else:
			p2 = list(self.get_RPNS()[i].set_all_places())[choice_index]
		print "P2 = ", p2

		if new_p1: self.get_RPNS()[i].addResizablePlace(p1)
		if new_p2: self.get_RPNS()[i].addResizablePlace(p2)

		existing_transition = Arc(p1,t) in self.get_RPNS()[i].set_all_Arcs() and  Arc(t,p2) in self.get_RPNS()[i].set_all_Arcs() 
		# first_half = self.get_RPNS()[i].set_all_Arcs().intersection( Arc(p1,t) )
		# second_half = first_half.intersection( Arc(t,p2) ) 

		return p1,t,p2, existing_transition


	def dump_to_file(self, path):

		graph = pydot.Dot(self.Title, graph_type='digraph') 

		for v in self.RPNS:
			v.subDumpToFile(path, graph)

		graph.write_png(path)		


	def mutate_all_RPNS(self):
		print "*"*100
		for v in self.get_RPNS():
			print "Mutation individual", v
			E.mutate(v)


	def actual_crossover(self, t1, t2, v1, v2, debug=False):
		print "Exchange", t1, "and", t2

		# step 1: identify p_e and p_b for each transition
		preset_1  = v1.get_Preset_(t1)
		postset_1 = v1.get_Postset_(t1)
		pb1 = random.sample(preset_1, 1)[0]
		pe1 = random.sample(postset_1, 1)[0]

		print "Pb1:", pb1, "Pe1:", pe1

		preset_2  = v2.get_Preset_(t2)
		postset_2 = v2.get_Postset_(t2)
		pb2 = random.sample(preset_2, 1)[0]
		pe2 = random.sample(postset_2, 1)[0]

		print "Pb2:", pb2, "Pe2:", pe2

		# step 1: copy P+ (renaming)
		v2.addResizableTransition( t1 )
		v1.addResizableTransition( t2 )

		# E.dumpToFile("prova0_trans.png")

		""" COPY SUBSTRUCTURES """
		for p in preset_1:
			e = v1.get_Arc(Arc(p,t1))
			if isinstance(p, ResizablePlace):
				if p != pb1:					
					pnew = copy.deepcopy(p)
					if debug:
						pnew.name = "rp"+str(self.fetchUniquePlaceId()) + "(" + pnew.name + ")"
					else:
						pnew.name = "rp"+str(self.fetchUniquePlaceId()) 
					v2.addResizablePlace( pnew )
					v2.addArc( From=pnew, To=t1, weight=e.weight )					
				else:										
					v2.addArc( From=pb2, To=t1, weight=e.weight  )		
			else:				
				v2.addArc( From=p, To=t1, weight=e.weight )

		# E.dumpToFile("prova0_trans2.png")

		for p in preset_2:
			e = v2.get_Arc(Arc(p,t2))
			if isinstance(p, ResizablePlace):
				if p != pb2:
					pnew = copy.deepcopy(p)
					if debug:
						pnew.name = "rp"+str(self.fetchUniquePlaceId()) + "(" + pnew.name + ")"
					else:
						pnew.name = "rp"+str(self.fetchUniquePlaceId()) 
					v1.addResizablePlace( pnew )	
					v1.addArc( pnew, t2, weight=e.weight  )
				else:
					v1.addArc( pb1, t2, weight=e.weight  )
			else:
				v1.addArc( p, t2, weight=e.weight )

		# E.dumpToFile("prova0_trans3.png")

		for p in postset_1:
			e = v1.get_Arc(Arc(t1,p))
			if isinstance(p, ResizablePlace):
				if p != pe1:
					pnew = copy.deepcopy(p)
					if debug:
						pnew.name = "rp"+str(self.fetchUniquePlaceId()) + "(" + pnew.name + ")"
					else:
						pnew.name = "rp"+str(self.fetchUniquePlaceId())
					v2.addResizablePlace( pnew )
					v2.addArc( t1, pnew, weight=e.weight  )
				else:
					v2.addArc( t1, pe2, weight=e.weight  )					
			else:										
				v2.addArc( t1, p, weight=e.weight )				

		# E.dumpToFile("prova0_trans3.png")

		for p in postset_2:
			e = v2.get_Arc(Arc(t2,p))
			if isinstance(p, ResizablePlace):
				if p != pe2:
					pnew = copy.deepcopy(p)
					if debug:
						pnew.name = "rp"+str(self.fetchUniquePlaceId()) + "(" + pnew.name + ")"
					else:
						pnew.name = "rp"+str(self.fetchUniquePlaceId()) 
					v1.addResizablePlace( pnew )
					v1.addArc( t2, pnew, weight=e.weight  )
				else:
					v1.addArc( t2, pe1, weight=e.weight  )
			else:
				v1.addArc( t2, p, weight=e.weight )

		# E.dumpToFile("prova0_trans4.png")

		""" FINE: RIPULIAMO LE STRUTTURE """
		v1.safeRemoveResizableTransition(t1)
		v2.safeRemoveResizableTransition(t2)



	def crossover(self, v1, v2, debug=False):

		print "X"*100

		# step 1: choose two Resizable transitions
		pick_1 = random.sample(v1.set_resizable_Transitions(),1)[0]
		pick_2 = random.sample(v2.set_resizable_Transitions(),1)[0]
				
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
			best_fitness = self.RPNS[0]
			for s in sampled:
				if self.RPNS[s].FITNESS_VALUE < best_fitness:
					best_fitness = self.RPNS[s].FITNESS_VALUE
					best = s

			selected_population.append( self.RPNS[best] )



	def ranking(self):
		pass
	def roulette(self):
		pass

	def set_mutations_per_creation(self, n):
		print " * Will use",n,"mutations to create each HPN"
		self.mutationsPerCreation = n


	def set_population_size(self, s):
		if self.MODEL == None:
			print "ERROR: please specify a model before initializing the population"
			exit(-4)
		self.POP_SIZE = s
		print " * Population size set_ to", self.POP_SIZE
		self.createPopulation()

	def createPopulation(self):
		if self.POP_SIZE == 0:
			print "ERROR: please specify the population's size"
			exit(-5)
		for i in range(self.POP_SIZE):
			# p = ResizablePetriNet("V"+str(i))
			p = copy.deepcopy(self.MODEL)
			p.ID = "V"+str(i)
			self.addRPN(p)
		print " *", self.POP_SIZE, "RPNs added to EPN"



	def use_tournament(self, size=2):
		self.SEL_TYPE = self.USE_TOURNAMENT
		self.TOUR_SIZE = size
		print " * Selection mechanism: tournament with tournament size", size
	def use_ranking(self):
		self.SEL_TYPE = self.USE_RANKING
	def use_roulette(self):
		self.SEL_TYPE = self.USE_ROULETTE


	def set_static_model(self,sm):
		self.MODEL = sm


if __name__ == '__main__':
	
	random.seed(5)

	VM = ResizablePetriNet("model")
	VM.add_whole_transition( Place("input"), Transition("transizione"), Place("output") )

	E = EvolutionaryPetriNet()
	E.set_StaticModel(VM)
	E.set__population_size(10)
	E.uset_ournament(size=2)
	E.set_PreOrder(2)

	"""
	p0 = ResizablePetriNet("V0")
	p1 = ResizablePetriNet("V1")
	p2 = ResizablePetriNet("V2")
	"""

	"""
	vt0 = E.requestResizableTransition()
	vp0 = E.requestResizablePlace()
	vp1 = E.requestResizablePlace()
	vp2 = E.requestResizablePlace()
	vp3 = E.requestResizablePlace()
	vp4 = E.requestResizablePlace()
	vp5 = E.requestResizablePlace()

	p1.add_whole_transitionList([vp0], vt0, [vp2, vp3])
	p1.add_whole_transitionList([vp2], Transition("vera"), [vp1,Place("output")])
	p2.add_whole_transitionList([vp4, vp5], ResizableTransition("transizione"), [Place("output")])
	"""

	"""
	vt0 = E.requestResizableTransition()
	vt1 = E.requestResizableTransition()
	vp0 = E.requestResizablePlace()
	vp1 = E.requestResizablePlace()

	p1.add_whole_transitionList( [vp0], vt0, [Place("output")] )
	p1.add_place(Place("input"))
	p2.add_whole_transitionList( [Place("input")], vt1, [vp1] )
	p2.add_place(Place("output"))

	E.addRPN(p1)
	E.addRPN(p2)
	"""

	E.dumpToFile("EPN.png")
	
	"""
	for i in range(1,2):
		print "Iteration",i,"^"*100
		# E.set_RandomFitness()
		E.selection()
		E.crossover(p1,p2,debug=False)
		E.dumpToFile("prova"+str(i)+"a.png")
		E.mutateAllRPNS()
		E.dumpToFile("prova"+str(i)+"b.png")
	"""