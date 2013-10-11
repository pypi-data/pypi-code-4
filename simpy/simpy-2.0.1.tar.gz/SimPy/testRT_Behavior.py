#!/usr / bin / env python
from SimPy.SimulationRT import *
"""testRT_Behavior_OO.py
Tests SimulationRT for degree to which simulation time
and wallclock time can be synchronized.

Non-OO API.
"""
# $Revision: 295 $ $Date: 2009-03-30 14:26:20 +0200 (Mo, 30 Mrz 2009) $

print "Under test: SimulationRT.py %s"% version
__version__ = '2.0 $Revision: 295 $ $Date: 2009-03-30 14:26:20 +0200 (Mo, 30 Mrz 2009) $ '
print 'testRT_Behavior.py %s'%__version__

class Ticker(Process):
    def tick(self):
        self.timing = []
        while True:
            yield hold,self,1
            tSim = now()
            tRT = rtnow()
            self.timing.append((tSim,tRT))
            
initialize()
t=Ticker()
activate(t,t.tick())
simulate(until=10,real_time=True,rel_speed=1)

print "Speed ratio set: 1"
print "------------------"
for tSim,tRT in t.timing:
    print "tSim:%s, tRT:%s, speed ratio:%s"%(tSim,tRT,tSim/tRT)
      
initialize()
t=Ticker()
activate(t,t.tick())
simulate(until=10,real_time=True,rel_speed=5)

print
print "Speed ratio set: 5"
print "------------------"
for tSim,tRT in t.timing:
    print "tSim:%s, tRT:%s, speed ratio:%s"%(tSim,tRT,tSim/tRT)
