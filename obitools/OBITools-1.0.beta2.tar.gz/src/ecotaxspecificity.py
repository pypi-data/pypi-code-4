#!/usr/local/bin/python
'''
:py:mod:`ecotaxspecificity`: Evaluates barcode resolution
=========================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

The :py:mod:`ecotaxspecificity` command evaluates barcode resolution at different 
taxonomic ranks. 

As inputs, it takes a sequence record file annotated with taxids in the sequence 
header, and a database formated as an ecopcr database (see :doc:`obitaxonomy 
<obitaxonomy>`) or a NCBI taxdump (see NCBI ftp site).

An example of output is reported below::

                Number of sequences added in graph: 284
                Number of nodes in all components: 269
                Number of sequences lost: 15!
                rank                      taxon_ok      taxon_total     percent
                order                            8               8        100.00
                superfamily                      1               1        100.00
                parvorder                        1               1        100.00
                subkingdom                       1               1        100.00
                superkingdom                     1               1        100.00
                kingdom                          3               3        100.00
                phylum                           5               5        100.00
                infraorder                       1               1        100.00
                subfamily                        3               3        100.00
                class                            6               6        100.00
                species                         35             176         19.89
                superorder                       1               1        100.00
                suborder                         1               1        100.00
                subtribe                         1               1        100.00
                subclass                         3               3        100.00
                genus                            9              15         60.00
                superclass                       1               1        100.00
                family                          10              10        100.00
                tribe                            2               2        100.00
                subphylum                        1               1        100.00


In this example, the input sequence file contains 284 sequence records, but only 
269 have been examined, because taxonomic information was not recovered for the
the 15 remaining ones.

"Taxon_total" refers to the number of different taxa observed at this rank 
in the sequence record file (when taxonomic information is available at this 
rank), and "taxon_ok" corresponds to the number of taxa that the barcode sequence
identifies unambiguously in the taxonomic database. In this example, the sequence 
records correspond to 176 different species, but only 35 of these have specific 
barcodes. "percent" is the percentage of unambiguously identified taxa among 
the total number of taxa (taxon_ok/taxon_total*100).

'''

import math
import sys


from obitools.graph import Graph
from obitools.utils import progressBar
from obitools.align import LCS
from obitools.align import isLCSReachable
from obitools.format.options import addInputFormatOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from obitools.graph.algorithms.component import componentIterator
from obitools.ecopcr.options import addTaxonomyDBOptions, loadTaxonomyDatabase



def addSpecificityOptions(optionManager):
    group = optionManager.add_option_group('ecotaxspecificity specific options')
    group.add_option('-e','--errors',
                             action="store", dest="dist",
                             metavar="###",
                             type="int",
                             default=1,
                             help="Maximum errors between two sequences")
    group.add_option('-q','--quorum',
                            action="store", dest="quorum",
                            type="float",
                            default=0.0,
                            help="Quorum")


if __name__=='__main__':

    optionParser = getOptionManager([addInputFormatOption,addTaxonomyDBOptions,addSpecificityOptions])
    
    (options, entries) = optionParser()
    
    loadTaxonomyDatabase(options)
    tax =options.taxonomy
    
    ranks = set(x for x in tax.rankIterator())
    results = [seq for seq in entries]
    
    graph = Graph("error",directed=False)
    xx = 0
    for s in results:
        #if options.sample is None:
        #    sample = {"XXX":s['count'] if 'count' in s else 1}
        #else:
        #    sample = s[options.sample]
        #graph.addNode(s.id,shape='circle',_sequence=s,_sample=sample)
        graph.addNode(s.id,shape='circle',_sequence=s)
        xx = xx + 1
    
   
    ldb = len(results)    
    digit = int(math.ceil(math.log10(ldb)))
    aligncount = ldb*(ldb+1)/2
    edgecount = 0
    print >>sys.stderr
    
    header = "Alignment  : %%0%dd x %%0%dd -> %%0%dd " % (digit,digit,digit)
    progressBar(1,aligncount,True,"Alignment  : %s x %s -> %s " % ('-'*digit,'-'*digit, '0'*digit))
    pos=1
    aligner = LCS()
    

    for i in xrange(ldb):

        inode = graph[results[i].id]
        
        aligner.seqA = results[i]
        li = len(results[i])
        
        for j in xrange(i+1,ldb):
            progressBar(pos,aligncount,head=header % (i,j,edgecount))
            pos+=1
            
            lj = len(results[j])
            
            lm = max(li,lj)
            lcsmin = lm - options.dist
            
            if isLCSReachable(results[i],results[j],lcsmin):
                aligner.seqB=results[j]
                ali = aligner()
                llcs=ali.score
                lali = len(ali[0])
                obsdist = lali-llcs
                if obsdist <= options.dist: # options.dist:
                    jnode = graph[results[j].id]
                    res=graph.addEdge(inode.label, jnode.label) # make links
                    edgecount+=1               

    indexbyseq={} # each element in this dict will be one component, with first seq of component as its key

    yy = 0
    for c in componentIterator(graph):
        sub = graph.subgraph(c)
        first = True
        s = ""
        for node in sub: #all nodes of a component should go with same key (taken as first sequence in comp)
            #print node
            seq = node["_sequence"]
            if first == True: #we will take first seq of a component as key for that component
                s = str(seq)
                indexbyseq[s]=set([seq])
                first = False
            else:
                indexbyseq[s].add(seq)
            yy = yy + 1
    
    #print "Number of sequences added in graph: " + str(xx)
    #print "Number of nodes in all components: " + str (yy)
    #print "Number of sequences lost: " + str (xx-yy) + "!"
    
    print >>sys.stderr
    
    # since multiple different sequences have one key, we need to know what that key is for each sequence
    indexbykey={} #it will have elements like: {"seq1":key, "seq2":key, ...} where 'key' is the component key to which 'seqx' belongs
    for key in indexbyseq.keys (): # loop on all components
        for x in indexbyseq[key]: # loop on each seq in this component
            v = str(x)
            if v not in indexbykey:
                indexbykey[v] = key
            
    print '%-20s\t%10s\t%10s\t%7s' % ('rank','taxon_ok','taxon_total','percent')
    lostSeqs = []
    for rank,rankid in ranks:
        if rank != 'no rank':
            indexbytaxid={}
            for seq in results:
                t = tax.getTaxonAtRank(seq['taxid'],rankid)
                if t is not None: 
                    if t in indexbytaxid:
                        indexbytaxid[t].add(str(seq))
                    else:
                        indexbytaxid[t]=set([str(seq)])
                        
            taxoncount=0
            taxonok=0            
            for taxon in indexbytaxid:
                taxlist = set()
                taxonindividuals = {}
                for tag in indexbytaxid[taxon]:
                    if tag in indexbykey:
                        key = indexbykey[tag] #get component key for this seq
                        if options.quorum > 0.0:
                            for x in indexbyseq[key]:
                                txn = tax.getTaxonAtRank(x['taxid'],rankid)
                                if txn not in taxonindividuals:
                                    taxonindividuals[txn] = set([x['taxid']])
                                else:
                                    taxonindividuals[txn].add(x['taxid'])
                        taxlist |=set(tax.getTaxonAtRank(x['taxid'],rankid) for x in indexbyseq[key])
                    else:
                        if tag not in lostSeqs:
                            lostSeqs.append(tag)
                    
                taxoncount+=1
                
                if options.quorum > 0.0:
                    max = 0
                    sum = 0
                    for k in taxonindividuals.keys ():
                        if len(taxonindividuals[k]) > max:
                            max = len(taxonindividuals[k])
                        sum = sum + len(taxonindividuals[k])
                    if max >= (sum-sum*options.quorum):
                        taxonok += 1
                else:
                    if len(taxlist)==1:
                        taxonok+=1
            if taxoncount:
                print '%-20s\t%10d\t%10d\t%8.2f' % (rank,taxonok,taxoncount,float(taxonok)/taxoncount*100)
     
   # if len (lostSeqs) > 0:            
     #   print "Lost Sequences:"
       # print lostSeqs       
    
            
            
    
    
