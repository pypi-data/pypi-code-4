"""
A new implementation of grid queue that starts a process and listens
for actions to complete via a pipe.
"""
import random
import PriorityQueue #lucio's implementation
import sys
import math
import time

def listen(gq, pipe):
    #print "GQ",self.my_index,"listening. pipe =",pipe
    #sys.stdout.flush()
    while True:
        action = pipe.recv()            
        #print "GQ",gq.my_index,"action:",action
        if action == "recruit":
            pipe.send(gq.recruit())
        elif action == "enquire":
            pipe.send(gq.enquire(pipe.recv()))
        elif action == "add":
            gq.add(pipe.recv())
        elif action == "remove":
            gq.remove(pipe.recv())
        elif action == "contains":
            pipe.send(gq.contains(pipe.recv()))
        elif action == "queue":
            pipe.send(gq.my_agents)
        elif action == "time":
            gq.time = pipe.recv()
        elif action == "terminate":
            break
        else:
            raise ValueError, "GridQueue received unknown action:" + action


class GridQueue():

    def __init__(self, top, bottom, gender, index, hazard):
        self.top = top
        self.bottom = bottom
        self.my_age = (top + bottom)/2
        self.my_gender = gender
        self.my_index = index
        self.hazard = hazard 

        #Data structures for keeping track of agents
        self.my_agents = PriorityQueue.PriorityQueue()  # populated with agents
        self.names = {}
        self.previous = None
        self.time = 0
        
    def recruit(self):
        """
        Returns the top (int) of the matching priority queue
        """
        #0. return agents for main queue (if any)
        if self.my_agents.empty(): 
            #print "  GQ",self.my_index,"return empty"
            return None
        
        #1. reorganize if dissimilar from previous
        if self.previous is not None: 
            #print "   ->had to rearrange"
            self.previous = None
            agents = list(self.my_agents.heap)  # copy the list
            self.my_agents.clear()
            for hazard, agent in agents:
                self.my_agents.push(agent.last_match,agent)
        
        agent = self.my_agents.pop()[1]
        if agent.last_match == self.time:
            self.my_agents.push(self.time,agent)
            #print "  GQ",self.my_index,"returned once already", agent.last_match, self.time
            return  None  # already returned on this round
        else:
            agent.last_match = self.time
            self.my_agents.push(agent.last_match,agent) 
            #print "  GQ",self.my_index,"returned", agent
            #self.my_agents.push(agent.last_match,agent_name) #put him/her back in queue with lower priority
            #print "   ->GQ Agent",a.attributes["NAME"],"recruited from", self.my_index,":","".join([str(agent.attributes["NAME"]) + ", " for p,agent in self.my_agents.queue])
            return agent.attributes["NAME"]

    def enquire(self, suitor):
        """
        Takes a suitor_name (int) returns a match_name (int) or None
        """
        #1. EMPTY QUEUE
        if self.my_agents.empty():
            #print "  GQ",self.my_index,"finished 1"
            #sys.stdout.flush()
            return None
        
        #2. RE-SORT IF DISSIMILAR
        if self.previous is None or self.previous.grid_queue != suitor.grid_queue:
            #print "  GQ",self.my_index,"reshuffling"
            #sys.stdout.flush()
            #self.previous = suitor
            #do the math just once
            suitor_age = self.age(suitor)
            mean_age = (suitor_age + self.my_age) / 2
            age_difference = suitor_age - self.my_age

            #flip coins for agents
            agents = list(self.my_agents.heap)
            self.my_agents.clear()
            for old_hazard, agent in agents:  # old_hazard is not needed
                #hazard = self.master.master.hazard(agent, suitor, age_difference, mean_age)
                hazard = self.hazard(agent, suitor, age_difference, mean_age)
                sys.stdout.flush()
                decision = int(random.random() < hazard)
                #self.my_agents.put((-decision, agent))
                self.my_agents.push(-decision,agent)
        self.previous = suitor

        #3. ADD ACCEPTING AGENT TO QUEUE
        top = self.my_agents.top()
        accept = top[0]
        match = top[1]
        match_name = match.attributes["NAME"]

        if(match == suitor or accept == 0):  # don't match self or unaccepting
            if accept == 0:  
                #print "  GQ",self.my_index,"finished 2"
                return None
            else:  
                raise NotImplementedError,"match == suitor"
        #print "    GQ",self.my_index,"is returning",match_name, match.attributes["NAME"]#,"my_agents now is",[str(a.attributes["NAME"]) + ", " for p,a in self.my_agents]
        return match_name
            
    def add(self, agent):
        agent_name = agent.attributes["NAME"]
        if agent_name in self.names.keys() and self.names[agent_name]:
            return  # sometimes these requests get sent too fast
        
        self.names[agent_name] = agent
        if self.previous is not None:
            # adding to "matching" queue
            self.my_agents.push(-1, agent)        
        else:
            # adding to a "time since last" queue
            self.my_agents.push(agent.last_match, agent)
            
    def remove(self, agent_name):
        #print "==> remove agent_name",agent_name," | "," ".join(self.agents_in_queue())
        sys.stdout.flush()
        self.my_agents.remove(self.names[agent_name])
        self.names[agent_name] = None
        
    def contains(self, agent_name):
        agent = self.names[agent_name]
        return self.my_agents.contains(agent)        
        
    def accepts(self,agent):
        return self.age(agent) >= self.bottom and self.age(agent) < self.top
        
    def age(self,agent):
        return (self.time - agent.born)/52           
            
    #Functions for debuging
    def agents_in_queue(self):
        return [str(a.attributes["NAME"]) for p,a in self.my_agents.heap]
