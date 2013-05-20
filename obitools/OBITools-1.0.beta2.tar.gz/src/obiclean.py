#!/usr/local/bin/python

'''
:py:mod:`obiclean`: Tags a set of sequences for PCR/sequencing errors identification 
====================================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obiclean` is a command that classifies sequence records either as ``head``, ``internal`` or ``singleton``.

For that purpose, two pieces of information are used:
    - sequence record counts
    - sequence similarities

*S1* a sequence record is considered as a variant of *S2* another sequence record if and only if:
    - ``count`` of *S1* divided by ``count`` of *S2* is lesser than the ratio *R*.
      *R* default value is set to 1, and can be adjusted between 0 and 1 with the ``-r`` option.
    - both sequences are *related* to one another (they can align with some differences, 
      the maximum number of differences can be specified by the ``-d`` option).

Considering *S* a sequence record, the following properties hold for *S* tagged as:
    - ``head``: 
       + there exists **at least one** sequence record in the dataset that is a variant of *S*
       + there exists **no** sequence record in the dataset such that *S* is a variant of this 
         sequence record
    - ``internal``:
       + there exists **at least one** sequence record in the dataset such that *S* is a variant
         of this sequence record
    - ``singleton``: 
       + there exists **no** sequence record in the dataset that is a variant of *S*
       + there exists **no** sequence record in the dataset such that *S* is a variant of this 
         sequence record

By default, tagging is done once for the whole dataset, but it can also be done sample by sample
by specifying the ``-s`` option. In such a case, the counts are extracted from the sample 
information.

Finally, each sequence record is annotated with three new attributes ``head``, ``internal`` and 
``singleton``. The attribute values are the numbers of samples in which the sequence record has 
been classified in this manner.
'''

from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.options import getOptionManager
from obitools.graph import Graph
from obitools.utils import progressBar
from obitools.align import LCS
from obitools.align import isLCSReachable


import sys
import math


def addCleanOptions(optionManager):
    optionManager.add_option('-d','--distance',
                             action="store", dest="dist",
                             metavar="###",
                             type="int",
                             default=1,
                             help="Maximum numbers of errors between two variant sequences [default: 1]")
    optionManager.add_option('-s','--sample',
                             action="store", dest="sample",
                             metavar="<TAGNAME>",
                             type="str",
                             default=None,
                             help="Tag containing sample descriptions")
     
    optionManager.add_option('-r','--ratio',
                             action="store", dest="ratio",
                             metavar="<FLOAT>",
                             type="string",
                             default="1.0",
                             help="Minimum ratio between counts of two sequence records so that the less abundant "
                                  "one can be considered as a variant of the more abundant "
                                  "[default: 1, i.e. all less abundant sequences are variant]")
    
    optionManager.add_option('-H','--head',
                             action="store_true", dest="head",
                             default=False,
                             help="Outputs only head tagged sequence records")
    
def lookforFather(node,sample):
    father=set()
    
    for neighbour in node.neighbourIterator():
        if sample in neighbour['_sample']:
            if neighbour['_sample'][sample] > node['_sample'][sample]:
                gdfather = lookforFather(neighbour, sample)
                father|=gdfather
    if not father:
        father.add(node)
        
    return father

def cmpseqcount(s1,s2):
    if 'count' not in s1:
        s1['count']=1
    if 'count' not in s2:
        s2['count']=1
    
    return cmp(s2['count'],s1['count'])


if __name__ == '__main__':
    
    optionParser = getOptionManager([addCleanOptions,addInOutputOption], progdoc=__doc__)
    (options, entries) = optionParser()
    
    try:
        options.ratio = (float(options.ratio),)
    except ValueError:
        options.ratio = eval(options.ratio)
    
    db = [s for s in entries]
  
    writer = sequenceWriterGenerator(options)
  
    graph = Graph("error",directed=False)
    for s in db:
        if options.sample is None:
            sample = {"XXX":s['count'] if 'count' in s else 1}
        else:
            sample = s[options.sample]
        graph.addNode(s.id,shape='circle',_sequence=s,_sample=sample)
    
    ldb = len(db)    
    digit = int(math.ceil(math.log10(ldb)))
    aligncount = ldb*(ldb+1)/2
    edgecount = 0
    print >>sys.stderr
    
    header = "Alignment  : %%0%dd x %%0%dd -> %%0%dd " % (digit,digit,digit)
    progressBar(1,aligncount,True,"Alignment  : %s x %s -> %s " % ('-'*digit,'-'*digit, '0'*digit))
    pos=1
    aligner = LCS()
    

    for i in xrange(ldb):

        inode = graph[db[i].id]
        aligner.seqA = db[i]
        li = len(db[i])
        
        for j in xrange(i+1,ldb):
            progressBar(pos,aligncount,head=header % (i,j,edgecount))
            pos+=1
            
            lj = len(db[j])
            
            lm = max(li,lj)
            lcsmin = lm - options.dist
            
            if isLCSReachable(db[i],db[j],lcsmin):
                aligner.seqB=db[j]
                ali = aligner()
                llcs=ali.score
                lali = len(ali[0])
                obsdist = lali-llcs
                if obsdist >= 1 and obsdist <= options.dist:
                    jnode = graph[db[j].id]
                    graph.addEdge(inode.label, jnode.label)
                    edgecount+=1               
            
    print >>sys.stderr
    
    ratio = []
    for node in graph.nodeIterator():
        for sample in node['_sample']:
            lratio = []
            for neighbour in node.neighbourIterator():
                if sample in neighbour['_sample'] :
                    if neighbour['_sample'][sample] > node['_sample'][sample]:
                        lratio.append((neighbour['_sample'][sample],node['_sample'][sample]))
            llratio=len(lratio)
            
            for r in lratio:
                ratio.append(r + (llratio,))
                        
    rfile = open('ratio.txt','w')
    for r in ratio:
        print >>rfile,"%-8d %-8d %-8d"  % r
    rfile.close()
    
    gfile = open('obiclean.dot','w')
    print >>gfile,graph
    gfile.close()
    
    
    for ratio in options.ratio:
        for node in graph.nodeIterator():
            sequence = node['_sequence']    

            status={}
            fathers={}
            common={}
            
            for sample in node['_sample']:
                sampleid = (sample,round(ratio,2))
                son=False
                father=False
                for neighbour in node.neighbourIterator():
                    if sample in neighbour['_sample'] :
                        c = float(neighbour['_sample'][sample])/float(node['_sample'][sample])
                        if c > 1./ratio:
                            son|=True
                        if c < ratio:
                            father|=True
                if father and not son:
                    status[sampleid]='h'
                elif not father and not son:
                    status[sampleid]='s'
                else:
                    status[sampleid]='i'
                
                if options.head:  
                    if status[sampleid]=='i':
                        fathers[sampleid]=[x['_sequence'].id for x in lookforFather(node, sample)]
                    else:
                        fathers[sampleid]=[node['_sequence'].id]
                    
            if options.head:  
                for sa in fathers:
                    fathers[sa]=list(set(fathers[sa]))
                    for s in fathers[sa]:
                        sid = (s,round(ratio,2))
                        common[sid]=common.get(sid,0)+1
                
            i=0
            h=0
            s=0
            o=0
            
            
            for sampleid in status:
                if sampleid[1]==ratio:
                    o+=1
                    if   status[sampleid]=='i':
                        i+=1
                    elif status[sampleid]=='s':
                        s+=1
                    elif status[sampleid]=='h':
                        h+=1


            sequence = node['_sequence']    

            ### Should be removed ?            
            tmp = sequence.get('clean',{})
            tmp.update(status)
            
            tmp = sequence.get('head',{})
            tmp[ratio]=h
            
            tmp = sequence.get('internal',{})
            tmp[ratio]=i
            
            tmp = sequence.get('singleton',{})
            tmp[ratio]=s

            sequence['occurrence']=o
    
            if options.head:
                node['_sequence'].get('father',{}).update(fathers)
                node['_sequence'].get('fathers',{}).update(common)


    for node in graph.nodeIterator():
        writer(node['_sequence'])
                
            
            
            

            
    

