import Queue
import random
import GridQueue
import pickle
import time
import sys
import multiprocessing
import PriorityQueue


class RelationshipOperator():

    def __init__(self, master):
        self.master = master
        self.main_queue = PriorityQueue.PriorityQueue()
        self.grid_queues = []
        
        #make Grid Queues:
        start = time.time()
        for age in range(master.MIN_AGE, master.MAX_AGE, master.BIN_SIZE):
            for gender in range(master.GENDERS):
                bottom = age
                top = age+master.BIN_SIZE
                self.grid_queues.append(GridQueue.GridQueue(top, bottom, 
                                        gender, len(self.grid_queues),
                                        self.master.hazard))
        master.NUMBER_OF_GRID_QUEUES = len(self.grid_queues)
        #print "time to make grid queues",time.time() - start
        start = time.time()

        #start the GridQueues and add pipes
        self.pipes = {}
        for gq in self.grid_queues:
            pipe_top, pipe_bottom = multiprocessing.Pipe()
            p = multiprocessing.Process(target=GridQueue.listen,args=(gq,pipe_bottom))
            p.start()
            self.pipes[gq.my_index] = pipe_top
        #print "time to start grid queues",time.time() - start
        
    def step(self):
        #0. Dissolve relationships
        #print "DISSOLVE RELATIONS"
        network = self.master.network
        relationships = network.edges()
        for r in relationships:
            network.get_edge_data(r[0], r[1])["duration"] -= 1
            if(network.get_edge_data(r[0], r[1])["duration"] < 0):
                self.dissolve_relationship(r[0], r[1])
        
        #0. Update the clock of the GridQueues (processes AND originals)
        pipes = self.pipes.values()
        for pipe in pipes:
            pipe.send("time")
            pipe.send(self.master.time)
        
        #1. Recruit
        for i in range(int(self.master.MAIN_QUEUE_MAX * self.master.INITIAL_POPULATION)):  # *** do this better
            self.recruit()
            
        #2. Match
        #print "main queue = ",[a.attributes["NAME"] for p,a in self.main_queue.heap]
        self.previous = None
        #pool = multiprocessing.Pool()
        while(not self.main_queue.empty()):
            self.match()
        #pool.close()

    def recruit(self): 
        gq = self.grid_queues[random.randint(0, len(self.grid_queues) - 1)]
        self.pipes[gq.my_index].send("recruit")
        agent_name = self.pipes[gq.my_index].recv()
        if agent_name is not None:
            agent = self.master.agents[agent_name]
            self.main_queue.push(gq.my_index, agent)
            
    def match(self):
        #1. get next suitor and request matches for him/her from grid queues
        suitor = self.main_queue.pop()[1]

        #print "======"
        #print "suitor:", suitor        
        
        if self.master.network.degree(suitor) >= suitor.dnp:
            #print "  -suitor is no longer looking"
            return  # if they were matched before their turn in the main queue
        self.previous = suitor

        """
        #1.1 Sequential matches grab
        #start = time.time()
        #suitor_name = suitor.attributes["NAME"]
        matches = [GridQueue.pool_enquire(suitor,resort, gq) for gq in self.grid_queues]        
        matches = [self.master.agents[m] for m in matches if m is not None] #remove Nones
        #print "time waiting for results",time.time() - start

        #1.2 Parallel, parallel python using return value

        #1.3 Parallel, processes adding to queue

        #1.4 Parallel, pool using get method
        #pool = multiprocessing.Pool()
        
        results = []
        for gq in self.grid_queues:
            r = pool.apply_async(GridQueue.pool_enquire, (suitor, resort, gq))
            results.append(r)
            print "GQ",gq.my_index," submitted (0)",time.time()
        #matches = [r.get() for r in results]  # wait for to finish
        #DEBUG
        print "sleeping -->"
        for i in range(5):
            time.sleep(1)
            print i,
        print "<--- awake"
        sys.stdout.flush()
        matches = []
        for r in results:
            start2 = time.time()
            print "GQ",len(matches),"getting (0)",time.time()
            matches.append(r.get())
            print "GQ",len(matches)-1,"gotten (0)",time.time()
            end2 = time.time()
            print "  --> GQ",len(matches)-1,"total time (0)",end2 - start2
#            print "    g pool map time",starts[r]
#            print "    g start2",start2
#            print "    g end", end2
#            print "    g total",end2-start2
#        print "time waiting for results",time.time() - start
        matches = [self.master.agents[m] for m in matches if m is not None]
        #pool.close()
        """
        
        #1.5 Parallel, pool adding to queue -- NOPE -> Pools don't like queues/pipes

        #1.6 Parallel, send enquiries via pipe
        for pipe in self.pipes.values():
            pipe.send("enquire")
            pipe.send(suitor)
        names = [pipe.recv() for pipe in self.pipes.values()]        
        matches = [self.master.agents[n] for n in names if n is not None]
        
        #2. Suitor flips coins with potential matches
        #print "matches:",[m.attributes["NAME"] for m in matches]
        if(not matches): #no matches
            #print "   -Suitor had not matches"
            return
            
        pq = Queue.PriorityQueue()
        while(matches):
            match = matches.pop()
#            print " --> match",match
            hazard = self.master.hazard(suitor, match)
            r = random.random()
            decision = int(r < hazard)
            pq.put((-decision, match))
        
        #3. Verify acceptance and form the relationship
        top = pq.get()
        match = top[1]
        accept = top[0]
        if accept:
            #print "   -Suitor choose",match
            self.form_relationship(suitor, match) 
            if self.master.network.degree(suitor) >= suitor.dnp:
                #print "send remove for agent",suitor.attributes["NAME"],"place",1
                self.pipes[suitor.grid_queue].send("remove")
                self.pipes[suitor.grid_queue].send(suitor.attributes["NAME"])
            if self.master.network.degree(match) >= match.dnp:
                #print "send remove for agent",match.attributes["NAME"],"place",2
                self.pipes[match.grid_queue].send("remove")
                self.pipes[match.grid_queue].send(match.attributes["NAME"])
        else:
            #print "   -Suitor had no luck flipping coins"
            pass

            
    def form_relationship(self, agent1, agent2):
        d = self.duration(agent1, agent2)
        agent1.last_match = self.master.time
        agent2.last_match = self.master.time
        self.master.relationships.append((agent1, agent2, self.master.time, self.master.time + d))
        self.master.network.add_edge(agent1, agent2, {"duration": d})
        #print "  formation:",agent1.attributes["NAME"],agent2.attributes["NAME"]

    def dissolve_relationship(self, agent1, agent2):
        self.master.network.remove_edge(agent1, agent2)
        #print "dissolve relationship",agent1.attributes["NAME"], "age", \
#            self.master.age(agent1), agent2.attributes["NAME"], "age", \
#            self.master.age(agent2)
        
        #add agents into appropriate grid queues
        self.update_grid_queue_for(agent1)
        self.update_grid_queue_for(agent2)

    def duration(self, agent1, agent2):
        """
        A function that can test some qualities of the agents to assess what
        kind of relationship they would form (i.e., transitory, casual,
        marriage)
        """
        return random.randint(10, 20)  # initial naive duration calculation

    def update_grid_queue_for(self, agent):
        """
        Find the appropriate grid queue for agent. Called (1) by Time Operator
        when agent graduates to the next grid queue, (2) relationship operator
        dissolves a relationship or (3) by make_population in the mainloop
        """
        # 2nd predicate: agent already in the queue (trying to form multiple relationships)
        # 1st predicate:-- don't
        # try 2nd pred without first
#        agent_name = agent.attributes["NAME"]
#        #if self.master.grid_queue[agent] and self.master.grid_queue[agent].my_agents.contains(agent_name):
#        if agent.grid_queue:  # grid queue is "None" during make population 
#            grid_queue = self.grid_queues[agent.grid_queue]
#            self.pipes[agent.grid_queue].send("contains")
#            self.pipes[agent.grid_queue].send(agent_name)
#            if self.pipes[agent.grid_queue].recv():  # returns whether agent in gq
#                return

        # add to new
        #print "UPDATING:",agent.info()
        #print "UPDATING: agent",agent.attributes["NAME"],"age",self.master.age(agent)
    
        try:        
            grid_queue = [gq for gq in self.grid_queues if gq.accepts(agent)][agent.gender]
            #self.master.grid_queue[agent] = grid_queue
            agent.grid_queue = grid_queue.my_index
    #        self.pipes[grid_queue].send("add")
    #        self.pipes[grid_queue].send(agent_name)
            self.pipes[grid_queue.my_index].send("add")
            self.pipes[grid_queue.my_index].send(agent)
        except IndexError:
            print "agent",agent.attributes["NAME"],"age",self.master.age(agent)
            for gq in self.grid_queues:
                print " GQ",gq.my_index,"bottom",gq.bottom, "time",gq.time
            raise IndexError

class TimeOperator():

    def __init__(self, master):
        self.master = master

    def step(self):
        #sync grid_queue clocks
        for gq in self.master.relationship_operator.grid_queues:  # kinda hacky :(
            gq.time = self.master.time        
        
        #Increment ages of agents, move their queue if necessary
        agents = self.master.network.nodes()
        for agent in agents:
            agent_name = agent.attributes["NAME"]
            agent_pipe = self.master.relationship_operator.pipes[agent.grid_queue]
            agent_pipe.send("contains")
            agent_pipe.send(agent_name)
            #if too old
            #print "TIME STEPPING agent",agent_name,"age",self.master.age(agent)
            if self.master.age(agent) >= self.master.MAX_AGE:
                #print "  -->being removed"
                #remove
                
                #end ongoing relations
                relations = self.master.network.edges(agent)
                for r in relations:
                    other = [r[0],r[1]][r[0]==agent]
                    self.master.network.remove_edge(r[0], r[1])
                    if self.master.age(other) >= self.master.MAX_AGE: 
                        continue  # going to be removed later
                    #print "  >other",other.attributes["NAME"],"age",self.master.age(other)
                    self.master.relationship_operator.update_grid_queue_for(other)
                    
                #update grid queues
                in_grid_queue = agent_pipe.recv()
                if in_grid_queue:  # remove if still in GQ
                    #print "in_grid_queue?",in_grid_queue
                    sys.stdout.flush()
                    #print "send remove for agent",agent.attributes["NAME"],"place",3
                    agent_pipe.send("remove")
                    agent_pipe.send(agent_name) 
                agent.grid_queue = None                
                self.master.network.remove_node(agent)
                agent.attributes["TIME_REMOVED"] = self.master.time

                #replace
                self.master.make_population(size=1, born=lambda: self.master.time - (52*15))
                continue  # go to the next agent
                
            #if (in queue) and (shouldn't be)
            gq = self.master.relationship_operator.grid_queues[agent.grid_queue]
            if agent_pipe.recv() and not gq.accepts(agent):
                #print "send remove for agent",agent.attributes["NAME"],"place",4
                agent_pipe.send("remove")
                agent_pipe.send(agent_name) 
                self.master.relationship_operator.update_grid_queue_for(agent)

        #Relationship operator takes care of decrementing relationships


class InfectionOperator():

    def __init__(self, master):
        self.master = master

    def step(self):
        #Go through edges and flip coin for infections
        now = self.master.time
        relationships = self.master.network.edges()
        for r in relationships:
            #print "now:",now,"|",r[0].time_of_infection, r[0].time_of_infection<now, r[1].time_of_infection, r[1].time_of_infection>now
            if(r[0].time_of_infection < now and r[1].time_of_infection > now and random.random() < self.master.infectivity):
                r[1].time_of_infection = now
                continue
            if(r[1].time_of_infection < now and r[0].time_of_infection > now and random.random() < self.master.infectivity):
                r[0].time_of_infection = now

    def perform_initial_infections(self, initial_prevalence, seed_time):
        infections = int(initial_prevalence*self.master.INITIAL_POPULATION)
        for i in range(infections):
            agent = self.master.agents[random.randint(0, len(self.master.agents) - 1)]
            agent.time_of_infection = seed_time * 52
