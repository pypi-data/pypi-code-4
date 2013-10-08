import sys
import random
import math
import sets
import pydot
import copy
from rpn import *

class EvolutionaryPetriNet(object):

	def __init__(self, title=None):
		print "New empty EPN created"
		self.RPNS = []
		self.counter_Resizableplaces = 0
		self.counter_Resizabletransitions = 0
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
		self.counter_Resizabletransitions += 1
		return self.counter_Resizabletransitions
	def fetchUniquePlaceId(self):
		self.counter_Resizableplaces += 1
		return self.counter_Resizableplaces

	def requestResizableTransition(self):
		nvt = ResizableTransition("vt"+str(self.fetchUniqueTransitionId()))
		# print "New Resizable Transition requested:", nvt
		return nvt
	def requestResizablePlace(self):
		nrp = ResizablePlace("rp"+str(self.fetchUniquePlaceId()))		
		# print "New Resizable Place requested:", nrp
		return nrp


	def addRPN(self,v):
		self.RPNS.append(v)
		print "RPN '",v,"' added to EPN"


	def getRPNS(self):
		return self.RPNS


	def removeSingletons(self, i, list_places):
		""" 
			If a mutation or crossover removes all arcs from/to a Resizable place 
			contained in list_places, remove that place.
		"""		
		for p in list_places:
			# print "Checking arcs to",p
			# print self.getRPNS()[i].getArcsConnectedToNode(p)
			if len(self.getRPNS()[i].getArcsConnectedToNode(p))==0:
				self.getRPNS()[i].getResizablePlaces.remove(p)


	def randomlyModifyWeights(self, i, t):
		print "Mutation #8", "_"*100
		random_diff   = random.choice([-1,+1])	# == 0 ok? TODO
		p_arc = random.choice( self.getRPNS()[i].getArcsConnectedToNode(t) )
		# p_arc.weight += random_diff
		self.getRPNS()[i].setWeight(p_arc, p_arc.weight + random_diff)
	

	def cleanUpThings(self, t, idx=None):

		if idx!=None:
			self.verifyOrder(idx,t)
			pre  = self.getRPNS()[idx].getPreset(t)
			post = self.getRPNS()[idx].getPostset(t)
			self.removeSingletons(idx,pre)
			self.removeSingletons(idx,post)


	def actuallyMutate(self, v):
		index = 0
		if isinstance(v, ResizablePetriNet):
			index = self.getRPNS().index(v)
		else:
			index = v
		p1, t, p2, existing_triple = self.generateTriple(index)

		# mutation introduces a new transition (p1,t),(t,p2)
		# this could invalidate pre- and post-order conditions
		# moreover, we must identify mutation #8 TODO
		if existing_triple:
			self.randomlyModifyWeights(index,t)		
		else:			
			self.getRPNS()[index].addWholeTransition(p1,t,p2)
		
		self.cleanUpThings(t,idx=index)
		"""
		self.verifyOrder(index,t)
		pre  = self.getRPNS()[index].getPreset(t)
		post = self.getRPNS()[index].getPostset(t)
		self.removeSingletons(index,pre)
		self.removeSingletons(index,post)
		"""



	def mutate(self, v):
		"""
			Mutate an arbitrary RPN "v". This method mimickes a C++ overload.
			Returns the preset and postset modified by mutation.
		"""
		if isinstance(v, int):
			if len(self.getRPNS())-1<v:
				print "ERROR: RPN",v,"does not exist!"
				exit(-2)
		if isinstance(v, ResizablePetriNet):
			if v not in self.getRPNS():
				print "ERRO: RPN",v,"does not exist!"
				exit(-2)
		self.actuallyMutate(v)
		
	def verifyPreorder(self,i,t):
		if self.O_PRE == -1: return

		while(True):
			total = 0
			preset = self.getRPNS()[i].getPreset(t)
			for p in preset:
				total += self.getRPNS()[i].getWeight( Arc(p,t) )
			if total <= self.O_PRE:
				return
			else:
				print "Fixing pre-order of transition",t," (",total,")"

			picked_arc = Arc(random.choice(list(preset)),t)
			pa = self.getRPNS()[i].getArc(picked_arc)
			w = pa.weight
			self.getRPNS()[i].setWeight( pa , w-1 ) 
			"""print picked_arc
			w = self.getRPNS()[i].getWeight( picked_arc )	
			self.getRPNS()[i].setWeight( picked_arc , w-1 ) 
			"""

			if self.getRPNS()[i].getArcsConnectedToNode(picked_arc.start) == []:
				print "Singleton detected: removing", picked_arc.start
				# TODO: check whether it is Resizable or not
				try:
					self.getRPNS()[i].RP.remove(picked_arc.start)
				except:
					pass


	def verifyPreorderOld(self,i,t):
		if self.O_PRE == -1: return			
		while(True):
			total = 0
			preset = self.getRPNS()[i].getPreset(t)	
			for p in preset:
				total += self.getRPNS()[i].getWeight( Arc(p,t) )
			if total<=self.O_PRE:				
				return
			else:
				print "Fixing pre-order (",total,")"
			total_arcs = len( preset )
			picked_arc = random.randint(0, total_arcs)
			for n,a in enumerate(preset):
				if n==picked_arc:
					break
			w = self.getRPNS()[i].getWeight( Arc(a,t) )
			self.getRPNS()[i].setWeight( Arc(a,t) , w-1 ) 
			if self.getRPNS()[i].getArcsConnectedToNode(a) == []:
				print "Singleton detected: removing", a
				# TODO: check whether it is Resizable or not
				self.getRPNS()[i].RP.remove(a)


	def verifyPostorder(self,i,t):
		if self.O_POST == -1: return			
		while(True):
			total = 0
			postset = self.getRPNS()[i].getPostset(t)	
			for p in postset:
				total += self.getRPNS()[i].getWeight( Arc(t,p) )
			if total<=self.O_POST:				
				return
			else:
				print "Fixing post-order (",total,")"
			total_arcs = len( postset )
			picked_arc = random.randint(0, total_arcs)
			for n,a in enumerate(postset):
				if n==picked_arc:
					break
			w = self.getRPNS()[i].getWeight( Arc(t,a) )
			self.getRPNS()[i].setWeight( Arc(t,a) , w-1 ) 
			if self.getRPNS()[i].getArcsConnectedToNode(a) == []:
				print "Singleton detected: removing"
				# TODO: check whether it is Resizable or not
				self.getRPNS()[i].RP.remove(a)


	def verifyOrder(self,i,t):
		self.verifyPreorder(i,t)
		self.verifyPostorder(i,t)
		

	def prob_distribution_newplace(self, i):		
		tp = len(self.getRPNS()[i].getAllPlaces())		
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

		total_places = len(self.getRPNS()[i].getAllPlaces())
		total_prob = total_places +1
		choice = random.uniform(0,total_prob)
		choice_index = int(choice)
		if choice_index>=total_places:
			p1 = self.requestResizablePlace()
			new_p1 = True
			
		else:
			p1 = list(self.getRPNS()[i].getAllPlaces())[choice_index]
		print "P1 = ", p1

		# le transizioni che vengono toccate sono SOLO quelle Resizablei!
		total_transitions = len(self.getRPNS()[i].getResizableTransitions())
		total_prob = total_transitions +1
		choice = random.uniform(0,total_prob)
		choice_index = int(choice)
		if choice_index>=total_transitions:
			t = self.requestResizableTransition()
			self.getRPNS()[i].addResizableTransition(p1)
		else:
			t = list(self.getRPNS()[i].getResizableTransitions())[choice_index]
		print "T = ", t

		total_places = len(self.getRPNS()[i].getAllPlaces())
		total_prob = total_places +1
		choice = random.uniform(0,total_prob)
		choice_index = int(choice)
		if choice_index>=total_places:
			p2 = self.requestResizablePlace()
			new_p2 = True
			# self.getRPNS()[i].addResizablePlace(p1)
		else:
			p2 = list(self.getRPNS()[i].getAllPlaces())[choice_index]
		print "P2 = ", p2

		if new_p1: self.getRPNS()[i].addResizablePlace(p1)
		if new_p2: self.getRPNS()[i].addResizablePlace(p2)

		existing_transition = Arc(p1,t) in self.getRPNS()[i].getAllArcs() and  Arc(t,p2) in self.getRPNS()[i].getAllArcs() 
		# first_half = self.getRPNS()[i].getAllArcs().intersection( Arc(p1,t) )
		# second_half = first_half.intersection( Arc(t,p2) ) 

		return p1,t,p2, existing_transition


	def dumpToFile(self, path):

		graph = pydot.Dot(self.Title, graph_type='digraph') 

		for v in self.RPNS:
			v.subDumpToFile(path, graph)

		graph.write_png(path)		


	def mutateAllRPNS(self):
		for v in self.getRPNS():
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
		v2.addResizableTransition( t1 )
		v1.addResizableTransition( t2 )

		# E.dumpToFile("prova0_trans.png")

		""" COPY SUBSTRUCTURES """
		for p in preset1:
			e = v1.getArc(Arc(p,t1))
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

		for p in preset2:
			e = v2.getArc(Arc(p,t2))
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

		for p in postset1:
			e = v1.getArc(Arc(t1,p))
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

		for p in postset2:
			e = v2.getArc(Arc(t2,p))
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
		pick_1 = random.sample(v1.getResizableTransitions(),1)[0]
		pick_2 = random.sample(v2.getResizableTransitions(),1)[0]
				
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
			best_fitness = self.RPNS[0]
			for s in sampled:
				if self.RPNS[s].FITNESS_VALUE < best_fitness:
					best_fitness = self.RPNS[s].FITNESS_VALUE
					best = s
			a = copy.deepcopy(self.RPNS[best])
			selected_indeces.append(best)
			a.setID("V"+str(i))
			selected_population.append( a )
		print "Selected individuals:", selected_indeces		
		self.RPNS = selected_population
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
			# p = ResizablePetriNet("V"+str(i))
			p = copy.deepcopy(self.MODEL)
			p.ID = "V"+str(i)
			self.addRPN(p)
		print " *", self.POP_SIZE, "RPNs added to EPN"



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
		selected_pop = self.getRPNS()
		while(len(selected_pop)>0):
			print selected_pop			
			prob = random.random()
			if prob < self.PROB_REPRODUCTION:
				new_population.append(selected_pop.pop())
				print "Direct reproduction"
			else:
				if len(selected_pop)>1:										
					self.crossover(self.getRPNS()[0],self.getRPNS()[1])
					new_population.append(selected_pop.pop())
					new_population.append(selected_pop.pop())
					print "Crossover"
				else:
					new_population.append(selected_pop.pop())
					print "Direct reproduction"
		
		self.RPNS = copy.deepcopy(new_population)

	def main_mutation(self):
		for i in range(self.POP_SIZE):
			if random.random()<self.PROB_MUTATION:
				self.mutate(self.getRPNS()[i])

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
		best_fitness = self.getRPNS()[0].FITNESS_VALUE
		for i in range(1, self.POP_SIZE):
			if best_fitness>self.getRPNS()[0].FITNESS_VALUE:
				best_fitness = self.getRPNS()[0].FITNESS_VALUE
				best = i 
		return best, best_fitness