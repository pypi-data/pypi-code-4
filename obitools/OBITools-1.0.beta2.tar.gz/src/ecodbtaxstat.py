#!/usr/local/bin/python
'''
:py:mod:`ecodbtaxstat`: Gives taxonomic rank frequency of a given ``ecopcr`` database   
=====================================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

The :py:mod:`ecodbtaxstat` command requires an ``ecopcr`` database and a taxonomic rank 
(specified by the ``--rank`` option, default *species*). The command outputs first 
the total number of sequence records in the database having taxonomic information at this rank, 
and then the number of sequence records for each value of this rank.

'''

from obitools.options import getOptionManager

from obitools.options.taxonomyfilter import addTaxonomyFilterOptions,  \
                                            taxonomyFilterIteratorGenerator

from obitools.ecopcr.taxonomy import EcoTaxonomyDB
from obitools.ecopcr.sequence import EcoPCRDBSequenceIterator

def addRankOptions(optionManager):
    
    group = optionManager.add_option_group('ecodbtaxstat specific option')
    group.add_option('--rank',
                             action="store", dest="rank",
                             metavar="<taxonomic rank>",
                             type="string",
                             default="species",
                             help="The taxonomic rank at which frequencies have to be computed. " 
                                  "Possible values are: "
                                  "class, family, forma, genus, infraclass, infraorder, kingdom, "
                                  "order, parvorder, phylum, species, species group, "
                                  "species subgroup, subclass, subfamily, subgenus, subkingdom, "
                                  "suborder, subphylum, subspecies, subtribe, superclass, "
                                  "superfamily, superkingdom, superorder, superphylum, tribe or varietas. "
                                  "(Default: species)")


def cmptax(taxonomy):
    def cmptaxon(t1,t2):
        return cmp(taxonomy.getScientificName(t1),
                   taxonomy.getScientificName(t2))
    return cmptaxon

if __name__=='__main__':
    
    optionParser = getOptionManager([addRankOptions,addTaxonomyFilterOptions], progdoc=__doc__)
    
    
    (options, entries) = optionParser()


    filter = taxonomyFilterIteratorGenerator(options)
    seqdb = EcoPCRDBSequenceIterator(options.ecodb,options.taxonomy)

    stats = {}
    i=0
    tot=0
    for seq in filter(seqdb):
        tot+=1
        t = options.taxonomy.getTaxonAtRank(seq['taxid'],options.rank)
        if t is not None:
            i+=1
            stats[t]=stats.get(t,0)+1
       
    print "#sequence count : %d" % tot
    print "#considered sequences : %d" % i     
    print "# %s : %d" % (options.rank,len(stats))
    taxons = stats.keys()
    taxons.sort(cmptax(options.taxonomy))
    
    for t in taxons:
        print "%s\t%d" % (options.taxonomy.getScientificName(t),stats[t])
    