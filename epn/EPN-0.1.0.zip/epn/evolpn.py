import sys
import random
import math
import sets
import pydot
import copy
from vpn import *

class EvolutionaryPetriNet(object):

	def __init__(self, title=None):
		print "New empty EPN created"
		self.VPNS = []
		self.counter_virtualplaces = 0
		self.counter_virtualtransitions = 0
		self.USE_UNIFORM_PROBABILITY = True

		# probabilities
		self.PROB_REPRODUCTION = 0.1
		self.PROB_CROSOVER = 0.9
		self.PROB_MUTATION = 0.99

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

	def setProbMutation(self, n):
		self.PROB_MUTATION = n

	def setProbCrossover(self, n):
		self.PROB_CROSSOVER = n 
		self.PROB_REPRODUCTION = 1.-n

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
		# print "New Virtual Transition requested:", nvt
		return nvt
	def requestVirtualPlace(self):
		nvp = VirtualPlace("vp"+str(self.fetchUniquePlaceId()))		
		# print "New Virtual Place requested:", nvp
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
		selected_indeces = []

		# for each individual
		for i in range(self.POP_SIZE):
			sampled = random.sample(range(0,self.POP_SIZE), self.TOUR_SIZE)		
			best = 0
			best_fitness = self.VPNS[0]
			for s in sampled:
				if self.VPNS[s].FITNESS_VALUE < best_fitness:
					best_fitness = self.VPNS[s].FITNESS_VALUE
					best = s
			a = copy.deepcopy(self.VPNS[best])
			selected_indeces.append(best)
			a.setID("V"+str(i))
			selected_population.append( a )
		print "Selected individuals:", selected_indeces		
		self.VPNS = selected_population
		# return selected_population



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

	def main_crossover(self):
		new_population = []
		selected_pop = self.getVPNS()
		while(len(selected_pop)>0):
			print selected_pop			
			prob = random.random()
			if prob < self.PROB_REPRODUCTION:
				new_population.append(selected_pop.pop())
				print "Direct reproduction"
			else:
				if len(selected_pop)>1:										
					self.crossover(self.getVPNS()[0],self.getVPNS()[1])
					new_population.append(selected_pop.pop())
					new_population.append(selected_pop.pop())
					print "Crossover"
				else:
					new_population.append(selected_pop.pop())
					print "Direct reproduction"
		
		self.VPNS = copy.deepcopy(new_population)

	def main_mutation(self):
		for i in range(self.POP_SIZE):
			if random.random()<self.PROB_MUTATION:
				self.mutate(self.getVPNS()[i])

	def optimize(self, iterations=1000):
		for i in range(iterations):
			self.selection()
			self.main_crossover()
			self.main_mutation()

		b, bf = self.getBest()
		print "Best solution found:", b, "with fitness:", bf
		return b, bf

	def getBest(self):
		best = 0
		best_fitness = self.getVPNS()[0].FITNESS_VALUE
		for i in range(1, self.POP_SIZE):
			if best_fitness>self.getVPNS()[0].FITNESS_VALUE:
				best_fitness = self.getVPNS()[0].FITNESS_VALUE
				best = i 
		return best, best_fitness