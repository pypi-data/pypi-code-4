#!/usr/local/bin/python
'''
:py:mod:`oligotag`: Designs a set of oligonucleotides with specified properties
=========================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>


:py:mod:`oligotag` designs a set of oligonucleotides that can be used for tagging a set 
of samples during PCR reactions, by adding the oligonucleotides on the 5' end of the primers.
Many options allow designing a set of oligonucleotides according to specified properties.
 
'''

import sys

from obitools.options import getOptionManager

from obitools import word

from obitools.word.options import addOligoOptions
from obitools.word.options import dnaWordIterator

from obitools.word import wordDist,decodeWord

from obitools.graph.algorithms.clique import cliqueIterator
from obitools.graph import Graph


def addOligoTagOptions(optionManager):
    
#    optionManager.add_option('-E','--bad-pairs',
#                             action="store", dest="badPairs",
#                             metavar="<filename>",
#                             type="str",
#                             help="filename containing a list of oligonucleotide")

    optionManager.add_option('-T','--timeout',
                             action="store", dest="timeout",
                             metavar="<seconde>",
                             type="int",
                             default=None,
                             help="timeout to identify a clique of good size")


    
def edgeIterator(words,distmin=1,error=None):
    words=[x for x in words]

    for i in xrange(len(words)):
        for j in xrange(i+1,len(words)):
            D = wordDist(words[i], words[j])
            if D>=distmin:
                yield words[i], words[j]
            elif error is not None:
                print >>error,words[i], words[j],D
                
            
def readData(edges):
    graph = Graph()
    
    for x,y in edges:
        graph.addEdge(x, y)
    return graph

    
if __name__=='__main__':
    

    optionParser = getOptionManager([addOligoOptions,addOligoTagOptions],
                                    )
    (options, entries) = optionParser()
    
#    if options.badPairs is not None:
#        error = open(options.badPairs,'w')
#    else:
    error = None
    
    goodOligo = dnaWordIterator(options)
        
    print >>sys.stderr,"Build good words graph..."

    graph= readData(edgeIterator(goodOligo,options.oligoDist,error))
    
    print >>sys.stderr,"Initial  graph size : %d  edge count : %d" % (len(graph),graph.edgeCount())
    print >>sys.stderr
    
    
    ci = cliqueIterator(graph, options.familySize,timeout=options.timeout)
    
    try:
        result = ci.next()
        print >>sys.stderr
                
        for word in result:
            print decodeWord(graph.getNode(index=word).getLabel(),options.oligoSize)
            
    except StopIteration:
        print >>sys.stderr
        print >>sys.stderr,"-------------------------------------------"
        print >>sys.stderr
        print >>sys.stderr,"No solutions for this parametter set"        
        print >>sys.stderr
        print >>sys.stderr,"-------------------------------------------"
        print >>sys.stderr
 
