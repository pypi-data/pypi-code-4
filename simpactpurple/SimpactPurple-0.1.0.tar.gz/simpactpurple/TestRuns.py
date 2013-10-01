# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 13:56:56 2013
s
@author: Lucio
"""


import Simpact

if __name__ == '__main__':
    #for i in range(10):  # run it ten time, hope for the error
    #   print "-------------------",i,"--------------------"
    s = Simpact.Simpact()
    s.MAX_AGE = 65 
    s.INITIAL_POPULATION = 100
    s.NUMBER_OF_YEARS = 30
    s.run(timing = True)
    
    #"""
    #GRAPH VERIFICATION
    import GraphsAndData
    GraphsAndData.prevalence_graph(s)
    GraphsAndData.formed_relations_graph(s)
    GraphsAndData.demographics_graph(s)
    GraphsAndData.age_mixing_graph(s)
    #"""

    #NETWORK GRAPHS
    #s = Simpact.Simpact()
    #s.INITIAL_POPULATION = 40
    #s.NUMBER_OF_YEARS = 1
    #s.run()
    GraphsAndData.sexual_network_graph(s)

    #POPULATION SIZE VS RUNTIME
    """
    import time
    print "population","runtime"
    for pop in range(100,1001,100):
        start = time.time()
        s = Simpact.Simpact()
        s.INITIAL_POPULATION = pop
        s.NUMBER_OF_YEARS = 30
        s.run()#
        end = time.time()
        print pop,end-start
    """
