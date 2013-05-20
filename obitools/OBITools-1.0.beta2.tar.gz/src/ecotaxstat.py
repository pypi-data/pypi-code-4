#!/usr/local/bin/python
'''
:py:mod:`ecotaxstat` : Getting the coverage of of an ecoPCR output compared to the original ecoPCR database
===========================================================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>


The :py:mod:`ecotaxstat` command requires two parameters : an ecoPCR formatted database (specified with the 
``-d``option) and an ecoPCR output (ideally computing on the specified ecoPCR database).

The command outputs for every ranks the coverage of the ecoPCR output, that is the fraction of taxids that 
have a sequence in the database and have also have a sequence in the ecoPCR output file.

Optionaly, taxids can be specified to focus the coverage on a smaller part of the taxonomy.

'''

from obitools.ecopcr import taxonomy
from obitools.ecopcr import sequence
from obitools.ecopcr import EcoPCRFile

from obitools.options import getOptionManager
from obitools.ecopcr.options import loadTaxonomyDatabase

import sys

def addTaxonomyOptions(optionManager):
        
    optionManager.add_option('-d','--ecopcrdb',
                             action="store", dest="db",
                             metavar="<FILENAME>",
                             type="string",
                             help="ecoPCR Database "
                                  "name")

    optionManager.add_option('-r','--required',
                             action="append", 
                             dest='required',
                             metavar="<TAXID>",
                             type="int",
                             default=[],
                             help="required taxid")

if __name__=='__main__':

    optionParser = getOptionManager([addTaxonomyOptions],
                                    entryIterator=EcoPCRFile)
    
    (options, entries) = optionParser()
    
    if (options.db is None):
        print>>sys.stderr, "-d option is required"
        sys.exit(1)

    if len(options.required)==0:
        print>>sys.stderr, "-r option is required"
        sys.exit(1)
    
    tax = taxonomy.EcoTaxonomyDB(options.db)
    seqd= sequence.EcoPCRDBSequenceIterator(options.db,taxonomy=tax)
    
    ranks = set(x for x in tax.rankIterator())
    
    listtaxonbyrank = {}
    
    for seq in seqd:
        taxid = seq['taxid']
        if (options.required and
            reduce(lambda x,y: x or y,
                      (tax.isAncestor(r,taxid) for r in options.required),
                      False)):

            for rank,rankid in ranks:
                if rank != 'no rank':
                    t = tax.getTaxonAtRank(seq['taxid'],rankid)
                    if t is not None:
                        if rank in listtaxonbyrank:
                            listtaxonbyrank[rank].add(t)
                        else:
                            listtaxonbyrank[rank]=set([t])
                        
    stats = dict((x,len(listtaxonbyrank[x])) for x in listtaxonbyrank)
    
    listtaxonbyrank = {}
        
    for seq in entries:
        for rank,rankid in ranks:
            if rank != 'no rank':
                t = tax.getTaxonAtRank(seq['taxid'],rankid)
                if t is not None:
                    if rank in listtaxonbyrank:
                        listtaxonbyrank[rank].add(t)
                    else:
                        listtaxonbyrank[rank]=set([t])

    dbstats= dict((x,len(listtaxonbyrank[x])) for x in listtaxonbyrank)
    
    ranknames = [x[0] for x in ranks]
    ranknames.sort()
    
    print '%-20s\t%10s\t%10s\t%7s' % ('rank','ecopcr','db','percent')
    
    for r in ranknames:
        if  r in dbstats and r in stats and dbstats[r]:
            print '%-20s\t%10d\t%10d\t%8.2f' % (r,dbstats[r],stats[r],float(dbstats[r])/stats[r]*100)
            
     

