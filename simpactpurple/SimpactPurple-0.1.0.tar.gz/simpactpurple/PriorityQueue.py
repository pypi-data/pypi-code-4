# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 18:32:35 2013

@author: Lucio
"""
from heapq import *
#from heapL import *
import multiprocessing

class PriorityQueue():

    def __init__(self):
        self.items = {}
        self.heap = []

    def push(self, priority, item):
        heappush(self.heap, (priority, item))
        self.items[item] = priority

    def pop(self):
        priority, item = heappop(self.heap)
        self.items[item] = None
        return (priority, item)
        
    def top(self):
        priority, item = heappop(self.heap)
        heappush(self.heap, (priority,item))
        return (priority, item)

    def remove(self, item):
        priority = self.items[item]
        self.heap.remove((priority, item))
        self.items[item] = None

    def contains(self, item):
        return item in self.items.keys() and self.items[item] is not None

    def clear(self):
        self.items = {}
        self.heap = []

    def empty(self):
        return not len(self.heap)
        
    def length(self):
        return len(self.heap)
        
    def __str__(self):
        return str(self.heap)

class ParallelPriorityQueue():

    def __init__(self,manager):
        #manager = multiprocessing.Manager()  # do I need a new instance of a manager?
        #global manager
        self.items = manager.dict()
        self.heap = manager.list()
        
    def push(self, priority, item):
        heappush(self.heap, (priority, item))
        self.items[item] = priority

    def pop(self):
        priority, item = heappop(self.heap)
        self.items[item] = None
        return (priority, item)
        
    def top(self):
        priority, item = heappop(self.heap)
        heappush(self.heap, (priority,item))
        return (priority, item)

    def remove(self, item):
        priority = self.items[item]
        self.heap.remove((priority, item))
        self.items[item] = None

    def contains(self, item):
        return item in self.items.keys() and self.items[item] is not None

    def clear(self):
        #self.__init__()
        while not self.empty():
            self.pop()

    def empty(self):
        return not len(self.heap)
        
    def length(self):
        return len(self.heap)
        
    def __str__(self):
        return str(self.heap)

class TestPriorityQueue():
#    pass
    def __init__(self):
        manager = Manager()
        self.dict = manager.dict()
        self.list = manager.list()
        
    def clear(self):
#        print "---in clear---"
#        print self.list
#        manager = Manager()
#        self.dict = manager.dict()
#        self.list = manager.list()
#        print self.list
#        print "--end clear---"
        while(self.list):
            self.list.pop()
        
    def addL(self, x):
        self.list.append(x)
        
    def addD(self, x, y):
        self.dict[x] = y
        
    def __str__(self):
        return str(self.list) + " | " + str(self.dict)