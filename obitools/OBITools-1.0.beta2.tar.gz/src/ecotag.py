#!/usr/local/bin/python
'''
:py:mod:`ecotag`: Assigns sequences to taxa
===========================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`ecotag` is the tool that assigns sequences to a taxon based on 
sequence similarity. The program first searches the reference database for the 
reference sequence(s) (hereafter referred to as 'primary reference sequence(s)') showing the 
highest similarity with the query sequence. Then it looks for all other reference 
sequences (hereafter referred to as 'secondary reference sequences') whose 
similarity with the primary reference sequence(s) is equal or higher than the 
similarity between the primary reference and the query sequences. Finally, it 
assigns the query sequence to the most recent common ancestor of the primary and 
secondary reference sequences. 

As input, `ecotag` requires the sequences to be assigned, a reference database 
in fasta format, where each sequence is associated with a taxon identified 
by a unique taxid, and a taxonomy database where taxonomic information is stored 
for each taxid.

  *Example:*
    
    .. code-block:: bash
        
          > ecotag -d embl_r113  -R ReferenceDB.fasta --sort=count -m 0.95 -r seq.fasta > seq_tag.fasta
    
    The above command specifies that each sequence stored in ``seq.fasta`` 
    is compared to those in the reference database called ``ReferenceDB.fasta`` 
    for taxonomic assignment. In the output file ``seq_tag.fasta``, the sequences 
    are sorted from highest to lowest counts. When there is no reference sequence 
    with a similarity equal or higher than 0.95 for a given sequence, no taxonomic 
    information is provided for this sequence in ``seq_tag.fasta``.

'''

from obitools.fasta import fastaNucIterator
#from obitools.align.ssearch import ssearchIterator
from obitools.utils.bioseq import uniqSequence,sortSequence

from obitools.align import lenlcs,ALILEN

from obitools.options.taxonomyfilter import addTaxonomyDBOptions,loadTaxonomyDatabase
from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption, sequenceWriterGenerator

import sys
import math
import os.path


def addSearchOptions(optionManager):
    
    optionManager.add_option('-R','--ref-database',
                             action="store", dest="database",
                             metavar="<FILENAME>",
                             type="string",
                             help="fasta file containing reference "
                                  "sequences")
        
#    optionManager.add_option('-s','--shape',
#                             action="store", dest="shape",
#                             metavar="shapeness",
#                             type="float",
#                             default=2.0,
#                             help="selectivity on the ssearch results "
#                                  "1.0 is the higher selectivity. "
#                                  "values > 1.0 decrease selectivity.")
    
    optionManager.add_option('-m','--minimum-identity',
                             action="store", dest="minimum",
                             metavar="identity",
                             type="float",
                             default=0.0,
                             help="minimum identity to consider.")
    
#    optionManager.add_option('-S','--normalized-smallest',
#                             action="store_false", dest="large",
#                             default=True,
#                             help="normalize identity over the shortest sequence")
#    
#    optionManager.add_option('-L','--normalized-largest',
#                             action="store_true", dest="large",
#                             default=True,
#                             help="normalize identity over the longest sequence")
    
    optionManager.add_option('-x','--explain',
                             action='store',dest='explain',
                             type="string",
                             default=None,
                             help="Add in the output CD (complementary data) record "
                                  "to explain identification decision")
    
    optionManager.add_option('-u','--uniq',
                             action='store_true',dest='uniq',
                             default=False,
                             help='Apply uniq filter on sequences before identification')
    
#    optionManager.add_option('-T','--table',
#                             action='store_true',dest='table',
#                             default=False,
#                             help='Write results in a tabular format')
    
#    optionManager.add_option('--store-in-db',
#                             action='store_true',dest='storeindb',
#                             default=False,
#                             help='Write results in an ecobarcode DB')
#    
#    optionManager.add_option('--update-db',
#                             action='store_true',dest='updatedb',
#                             default=False,
#                             help='Run identification only on new sequences')
    
    optionManager.add_option('--sort',
                             action='store',dest='sort',
                             type='string',
                             default=None,
                             help='Sort output on input sequence tag')
    
    optionManager.add_option('-r','--reverse',
                             action='store_true',dest='reverse',
                             default=False,
                             help='Sort in reverse order (should be used with -S)')
    
#    optionManager.add_option('-o','--output-sequence',
#                             action='store_true',dest='sequence',
#                             default=False,
#                             help='Add an extra column in the output with the query sequence')
#    
#    optionManager.add_option('--self-matches',
#                             action='store_true',dest='selfmatches',
#                             default=False,
#                             help='Switch to the new match algorithm')    

    optionManager.add_option('-E','--errors',
                             action='store',dest='error',
                             default=0.0,
                             help='Tolerated rate of wrong assignation')    


def count(data):
    rep = {}
    for x in data:
        if isinstance(x, (list,tuple)):
            k = x[0]
            if len(x) > 1:
                v = [x[1]]
                default=[]
            else:
                v = 1
                default=0
        else:
            k=x
            v=1
            default=0
        rep[k]=rep.get(k,default)+v
    return rep


def myLenlcs(s1, s2, minid, normalized, reference):

    if s1.hasKey('pairend_limit') :
        
        overlap = min(0,len(s1) - len(s2))
        
        f5P1 = s1[0:s1['pairend_limit']]
        f3P1 = s1[s1['pairend_limit']:]
        
        f5P2 = s2[0:s1['pairend_limit']]
        
        from2 = len(s2) - min(len(s2),len(f3P1))
        f3P2 = s2[from2:]
        
        errors = int(math.ceil((1-minid) * len(s1)))
        minid5P = max(len(f5P1),len(f5P2)) - errors
        minid3P = max(len(f3P1),len(f3P2)) - errors
             
        lcs5P, lali5P = lenlcs(f5P1,f5P2,minid5P,False)
        lcs3P, lali3P = lenlcs(f3P1,f3P2,minid3P,False)

        raw_lcs  = lcs5P  + lcs3P  - overlap
        lali = lali5P + lali3P - overlap
        lcs = raw_lcs / float(lali)
        
    else:     
        lcs, lali = lenlcs(s1,s2,minid,normalized,reference)

    return lcs, lali


#def lcsIterator(entries,db,options):
#    
#    for seq in entries:
#        results = []
#        maxid   = (None,0.0)
#        minid   = options.minimum
#        for d in db:
#            lcs,lali = myLenlcs(seq, d, minid,normalized=True,reference=ALILEN)
#            if lcs > maxid[1]:
#                maxid = (d,lcs)
#                minid = maxid[1] ** options.shape
#            results.append((d,lcs))
#        minid = maxid[1] ** options.shape
#        results = [x for x in results if x[1]>=minid]
#        yield seq,([maxid[0]],maxid[1]),results

def mostPreciseTaxid(taxidlist, options):
    tl = set(x for x in taxidlist if x > 1)
    if not tl:
        tl=set([1])
        
    while len(tl) > 1:
        t1 = tl.pop()
        t2 = tl.pop()
        if options.taxonomy.isAncestor(t1,t2):
            taxid = t2
        elif options.taxonomy.isAncestor(t2,t1):
            taxid = t1
        else:
            taxid = options.taxonomy.lastCommonTaxon(t1,t2)
        tl.add(taxid)
        
    taxid = tl.pop()
    
    return taxid
            
def lcsIteratorSelf(entries,db,options):
    
    for seq in entries:
        results = []
        maxid   = ([],0.0)
        minid   = options.minimum
        for d in db:
            lcs,lali = myLenlcs(seq,d,minid,normalized=True,reference=ALILEN)
            if lcs > maxid[1] and lcs > options.minimum:
                maxid = ([d],lcs)
                minid = maxid[1]
            elif lcs==maxid[1]:
                maxid[0].append(d)
                
        if maxid[0]:
            results.extend([(s,maxid[1]) for s in maxid[0]])
            for d in db:
                for s in maxid[0]:
                    if d.id != s.id:
                        lcs,lali = lenlcs(s,d,maxid[1],normalized=True,reference=ALILEN)      
                        if lcs >= maxid[1]:
                            results.append((d,lcs))
                
        yield seq,maxid,results
        
if __name__=='__main__':
    
    optionParser = getOptionManager([addSearchOptions,addTaxonomyDBOptions,addInOutputOption],progdoc=__doc__)
    
    (options, entries) = optionParser()
        
    taxonomy = loadTaxonomyDatabase(options)
    writer = sequenceWriterGenerator(options)
    
    print >>sys.stderr,"Reading reference DB ...",
#    if (hasattr(options, 'ecobarcodedb') and options.ecobarcodedb is not None):
#        try:
#            db = list(fastaNucIterator(options.database))
#        except IOError:
#            db = list(referenceDBIterator(options))  
#        if options.primer is not None:
#            entries = sequenceIterator(options)  
#    else:

    db = list(fastaNucIterator(options.database))
    dbname=os.path.splitext(os.path.basename(options.database))[0]

    print >>sys.stderr," : %d" % len(db)

    taxonlink = {}

    rankid = taxonomy.findRankByName(options.explain)
    
    for seq in db:
        id = seq.id[0:46]
        seq.id=id
        assert id not in taxonlink
        taxonlink[id]=int(seq['taxid'])
        
                
    if options.uniq:
        entries = uniqSequence(entries)
        
    if options.sort is not None:
        entries = sortSequence(entries, options.sort, options.reverse)

#    matcher = lcsIterator
#    
#    if options.selfmatches:
#        matcher= lcsIteratorSelf

    search = lcsIteratorSelf(entries,db,options)
                     
                    
    for seq,best,match in search:
        try:
            seqcount = seq['count']
        except KeyError:
            seqcount=1

        if best[0]:
            taxlist = set(taxonlink[p[0].id] for p in match)
            lca = taxonomy.betterCommonTaxon(options.error,*tuple(taxlist))
            scname = taxonomy.getScientificName(lca)
            rank = taxonomy.getRank(lca)
            if len(taxlist) < 15:
                species_list = set(taxonomy.getSpecies(t) for t in taxlist)
                species_list = [taxonomy.getScientificName(t) for t in species_list if t is not None]
            else:
                species_list = []
                
                
            worst = min(x[1] for x in match)
    
            data =['ID',seq.id,best[0][0].id,best[1],worst,'NA',seqcount,len(match),lca,scname,rank]
        else:
            data =['UK',seq.id,'NA','NA','NA','NA',seqcount,0,1,'root','no rank']
            
        tag = seq.get('id_status',{})
        tag[dbname]=data[0]=='ID'
        
        seq['count']=data[6]

        tag = seq.get('match_count',{})
        tag[dbname]=data[7]
        
        tag = seq.get('taxid_by_db',{})
        tag[dbname]=data[8]
        seq['taxid'] = mostPreciseTaxid(tag.values(), options)
        
        tag = seq.get('scientific_name_by_db',{})
        tag[dbname]=data[9]
        seq['scientific_name']=options.taxonomy.getScientificName(seq['taxid'])
        
        tag = seq.get('rank_by_db',{})
        tag[dbname]=data[10]
        seq['rank']=options.taxonomy.getRank(seq['taxid'])
        
        
        if data[0]=='ID':
            tag = seq.get('best_match',{})
            tag[dbname]=data[2]
        
            tag = seq.get('best_identity',{})
            tag[dbname]=data[3]

            tag = seq.get('species_list',{})
            tag[dbname]=species_list
        
            if options.explain is not None:
                tag = seq.get('explain',{})
                tag[dbname]=dict((s[0].id,s[1]) for s in match)
                
            

            seq['order']=options.taxonomy.getOrder(seq['taxid'])
            if seq['order']:
                seq['order_name']=options.taxonomy.getScientificName(seq['order'])
            else:
                seq['order_name']=None

            seq['family']=options.taxonomy.getFamily(seq['taxid'])
            if seq['family']:
                seq['family_name']=options.taxonomy.getScientificName(seq['family'])
            else:
                seq['family_name']=None
                
            seq['genus']=options.taxonomy.getGenus(seq['taxid'])
            if seq['genus']:
                seq['genus_name']=options.taxonomy.getScientificName(seq['genus'])
            else:
                seq['genus_name']=None
                
            seq['species']=options.taxonomy.getSpecies(seq['taxid'])
            if seq['species']:
                seq['species_name']=options.taxonomy.getScientificName(seq['species'])
            else:
                seq['species_name']=None
                        
        writer(seq)        
                    
                
                    
                
