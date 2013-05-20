#!/usr/local/bin/python
'''
:py:mod:`obitaxonomy`: Manages taxonomic databases
==================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org> and Celine Mercier <celine.mercier@metabarcoding.org>

The :py:mod:`obitaxonomy` command can generate an ecopcr database from a NCBI taxdump 
(see NCBI ftp site) and allows managing the taxonomic data contained in both types of 
database.

Several types of editing are possible:

**Adding a taxon to the database**

    The new taxon is described by three values: 
    its scientific name, its taxonomic rank, and the taxid of its first ancestor.
    Done by using the ``-a`` option. 
    
**Deleting a taxon from the database  /MARCHE PAS/**

    Erases a local taxon. Done by using the ``-D`` option and specifying a taxid. 
    
**Adding a species to the database**

    The genus of the species must already exist in the database. The species will be 
    added under its genus. Done by using the ``-s`` option and specifying a species 
    scientific name. 
    
**Adding a preferred scientific name for a taxon in the database (????)**

    Adds a preferred name for a taxon in the taxonomy, by specifying the new favorite 
    name and the taxid of the taxon whose preferred name should be changed (???). 
    Done by using the ``-f`` option.
    
**Adding all the taxa from a sequence file in OBITools extended fasta format to the database**

    All the taxon from a file in :doc:`OBITools extended fasta format <../fasta>`, and eventually their ancestors, are added to the 
    taxonomy database.
    
    The header of each sequence record must contain the attribute defined by the 
    ``-k`` option (default key: ``species_name``), whose value is the scientific name 
    of the taxon to be added.
    
    A taxonomic path for each sequence record can be specified with the ``-p`` option, 
    as the attribute key that contains the taxonomic path of the taxon to be added. 
    
    A restricting ancestor can be specified with the ``-A`` option, either as a taxid 
    (integer) or a key (string). If it is a taxid, this taxid is the default taxid 
    under which the new taxon is added if none of his ancestors are specified or can 
    be found. If it is a key, :py:mod:`obitaxonomy`: looks for the ancestor taxid in 
    the corresponding attribute, and the new taxon is systematically added under this 
    ancestor. By default, the restricting ancestor is the root of the taxonomic tree for
    all the new taxa.
    
    If neither a path nor an ancestor is specified in the header of the sequence record,
    :py:mod:`obitaxonomy` tries to read the taxon name as a species name and to find the 
    genus in the taxonomic database. If the genus is found, the new taxon is added under it. 
    If not, it is added under the restricting ancestor. 
    
    It is highly recommended to check what was exactly done by reading the output, 
    since :py:mod:`obitaxonomy` tries to be clever about what is done but can make 
    mistakes.
    
    Done by using the ``-F`` option. 

**Notes:**

- When a taxon is added, a new taxid is assigned to it. The minimum for the new taxids 
  can be specified by the ``-m`` option and is equal to 10000000 by default.

- For each modification, a line is printed with details on what was done.

'''


from obitools.options.taxonomyfilter import addTaxonomyDBOptions,loadTaxonomyDatabase
from obitools.options import getOptionManager
from obitools.ecopcr.taxonomy import ecoTaxonomyWriter
from obitools.fasta import fastaIterator, formatFasta
import sys


def addTaxonFromFile(name, rank, parent, options) :
    
    taxid = options.taxonomy.addLocalTaxon(name, rank, parent, options.taxashift)
    taxon = options.taxonomy.findTaxonByTaxid(taxid)
    parent= options.taxonomy._taxonomy[taxon[2]]
    
#    if options.write == '' :
    print>>sys.stderr, "added : %-40s\t%-15s\t%-8d\t->\t%s [%d] (%s)" % (taxon[3],options.taxonomy._ranks[taxon[1]],
                                                                            taxon[0],
                                                                            parent[3],parent[0],options.taxonomy._ranks[parent[1]])
#    else :
#        print>>options.write, "added : %-40s\t%-15s\t%-8d\t->\t%s [%d] (%s)" % (taxon[3],options.taxonomy._ranks[taxon[1]],
#                                                                           taxon[0],
#                                                                           parent[3],parent[0],options.taxonomy._ranks[parent[1]])
    return taxid


def numberInStr(s) :
    containsNumber = False
    for c in s :
        if c.isdigit() :
            containsNumber = True
    return containsNumber


def editTaxonomyOptions(optionManager):
    optionManager.add_option('-a','--add-taxon',
                             action="append", dest="newtaxon",
                             metavar="<taxon_name>:rank:parent",
                             default=[],
                             help="Adds a new taxon to the taxonomy. The new taxon "
                                  "is described by three values separated by colons: "
                                  "the scientific name, the rank of the new taxon, "
                                  "the taxid of the parent taxon")
    
    optionManager.add_option('-D','--delete-local-taxon',
                             action="append", dest="deltaxon",
                             metavar="<TAXID>",
                             default=[],
                             help="Erase a local taxon")

    optionManager.add_option('-s','--add-species',
                             action="append", dest="newspecies",
                             metavar="<SPECIES_NAME>",
                             default=[],
                             help="Adds a new species to the taxonomy. The new species "
                                  "is described by its scientific name")
    
    optionManager.add_option('-F','--add-file',
                             action="store", dest="species_file",
                             metavar="<file name>",
                             default=None,
                             help="Add all the species from a fasta file to the taxonomy. The header of"
                                  " the sequences must contain the field defined by the -S option")
    
    optionManager.add_option('-k','--key_name',
                             action="store", dest="key_name",
                             metavar="<key name>",
                             default='species_name',
                             help="Name of the attribute key used to find the species names in the headers "
                                  "when the -F option is used. "
                                  "Default = 'species_name'")
    
    optionManager.add_option('-f','--add-favorite-name',
                             action="append", dest="newname",
                             metavar="<taxon_name>:taxid",
                             default=[],
                             help="Add a new favorite name to the taxonomy. The new name "
                                  "is described by two values separated by a colon. "
                                  "the new favorite name and the taxid of the taxon")
                             
    optionManager.add_option('-m','--min-taxid',
                             action="store", dest="taxashift",
                             type="int",
                             metavar="####",
                             default=10000000,
                             help="minimal taxid for the newly added taxid")
    
    optionManager.add_option('-A','--restricting_ancestor',
                             action="store", dest="res_anc",
                             type="str",
                             metavar="<ANCESTOR>",
                             default='',
                             help="works with the -F option. Can be a word or a taxid (number). Enables to restrict the "
                                  "adding of taxids under a specified ancestor. If it's a word, it's the field containing "
                                  "the ancestor's taxid in each sequence's header (can be different for each sequence). If "
                                  "it's a number, it's the taxid of the ancestor (in which case it's the same for all the sequences)."
                                  " All the sequences in the file for which the genus can't be found will be added under this ancestor.")
    
#    optionManager.add_option('-w','--write_in_file',
#                             action="store", dest="write",
#                             metavar="<write_in_file>",
#                             type = "str", default='',
#                             help="works with the -F option. Writes all the taxa added in the specified file instead of in the console screen."
#                             " Useful for big and/or problematic files.")
    
    optionManager.add_option('-p','--path',
                             action="store", dest="path",
                             type="str",
                             metavar="<path>",
                             default='',
                             help="works with the -F option. Field name for the taxonomy path of the taxa if they are in the headers of the sequences. "
                             "Must be of the form 'Fungi, Agaricomycetes, Thelephorales, Thelephoraceae' with the highest ancestors"
                             " first and ', ' as separators between ancestors")
    
#    optionManager.add_option('-P','--force_ancestor',
#                             action="store_true", dest="force_ancestor",
#                             metavar="<force_ancestor>",
#                             default=False,
#                             help="works with the -A option when the ancestor is in the header. Forces the adding of the species under the ancestor specified."
#                             " /!\ the ancestor must exist. Use taxonomy paths (-p option) if you want the ancestor(s) to be created too.")
                             
if __name__ == '__main__':
    
    optionParser = getOptionManager([addTaxonomyDBOptions,editTaxonomyOptions])

    (options, entries) = optionParser()
    
    loadTaxonomyDatabase(options)
    
    localdata=False
    
    if options.write != '' :
        options.write = open(options.write, 'w')
    
    for t in options.newtaxon:
        tx = t.split(':')
        taxid = options.taxonomy.addLocalTaxon(tx[0].strip(),tx[1],tx[2],options.taxashift)
        taxon = options.taxonomy.findTaxonByTaxid(taxid)
        parent= options.taxonomy._taxonomy[taxon[2]]
        print "added : %-40s\t%-15s\t%-8d\t->\t%s [%d] (%s)" % (taxon[3],options.taxonomy._ranks[taxon[1]],
                                                     taxon[0],
                                                     parent[3],parent[0],options.taxonomy._ranks[parent[1]])
        localdata=True
    
#    for t in options.deltaxon:
#        tx = int(t)
#        taxon = options.taxonomy.removeLocalTaxon(tx)
#        print "removed : %-40s\t%-15s\t%-8d" % (taxon[3],options.taxonomy._ranks[taxon[1]],
#                                                     taxon[0])
#        localdata=True
    
    
    if options.species_file != None :
        
        useless_words = ['fungal','fungi','endophyte','unknown','mycorrhizal','uncultured','Uncultured','ectomycorrhiza', \
                         'ectomycorrhizal','mycorrhizal','vouchered','unidentified','bacterium','Bacterium']
        
        if options.res_anc == '' :
            restricting_ancestor = 1
            resAncInHeader = False
        elif options.res_anc.isdigit() :
            restricting_ancestor = int(options.res_anc)
            resAncInHeader = False
        else :
            resAncInHeader = True
            
        for seq in fastaIterator(options.species_file) :
            
            if resAncInHeader :
                if options.res_anc in seq :
                    restricting_ancestor = int(seq[options.res_anc])
                else :
                    restricting_ancestor = 1
            
            t = seq[options.key_name]
#            try :
#                taxid = options.taxonomy.findTaxonByName(t)[0]
#            except KeyError :
                
            if (resAncInHeader and options.res_anc in seq) :
                taxid = addTaxonFromFile(t,'species',restricting_ancestor,options)
       
            elif options.path != '' :   
                previous = options.taxonomy.findTaxonByTaxid(restricting_ancestor)
                if seq[options.path] != '' :
                    ancestors = [a for a in seq[options.path].split(', ')]
                    if ancestors[-1] != t :
                        ancestors.append(t)
                else :     # useful when data is from UNITE databases but could disappear
                    if len(t.split(' ')) >= 2 and not numberInStr(t) :
                        genus, trash = t.split(" ",1)
                        ancestors = [genus, t]
                    else :
                        ancestors = [t]
                for a in ancestors :
                    try:
                        previous = options.taxonomy.findTaxonByName(a)
                        taxid = previous[0]
                    except KeyError :
                        if (
                            options.taxonomy._ranks[previous[1]] == 'genus' 
                            or (a == ancestors[-1] 
                            and len(a.split(' ')) >= 2 
                            and ((not numberInStr(a))
                                 or 'sp' in a.split(' ') 
                                 or t[0].isupper()))
                            ) :                                 #super sale ca
                            
                            rank = 'species'
                        
                        elif (len(ancestors) > 1 and a == ancestors[-2] and len(ancestors[-1].split(' ')) >= 2 \
                              and ((not numberInStr(a)) or 'sp' in a.split(' '))) :      #a voirrrrr, trop restrictif ?
                            rank = 'genus'
                        else :
                            rank = 'no rank'
                        taxid = addTaxonFromFile(a,rank,previous[0],options)
                        previous = (taxid, options.taxonomy.findRankByName(rank))
                    
            else :
                
                if (len(t.split(' ')) >= 2 and (not numberInStr(t)  or 'sp' in t.split(' ') or t[0].isupper()) \
                    and t.split(' ')[0] not in useless_words) :
                    genus,species = t.split(" ",1)
                    try :
                        options.taxonomy.findTaxonByName(genus)
                    except KeyError :
                        taxid = addTaxonFromFile(genus,'genus',restricting_ancestor,options)
                    
                    parent = options.taxonomy.findTaxonByName(genus)
                    taxid = addTaxonFromFile(t, 'species', parent[0], options)
                    
                else :
                    taxid = addTaxonFromFile(t, 'species', restricting_ancestor, options)
            
            localdata=True
                
#            seq['taxid'] = taxid
#            print formatFasta(seq)
            

        
    for t in options.newspecies:
        genus,species = t.split(" ",1)
        parent = options.taxonomy.findTaxonByName(genus)
        taxid = options.taxonomy.addLocalTaxon(t,'species',parent[0],options.taxashift)
        taxon = options.taxonomy.findTaxonByTaxid(taxid)
        parent= options.taxonomy._taxonomy[taxon[2]]
        print "added : %-40s\t%-15s\t%-8d\t->\t%s [%d] (%s)" % (taxon[3],options.taxonomy._ranks[taxon[1]],
                                                     taxon[0],
                                                     parent[3],parent[0],options.taxonomy._ranks[parent[1]])
        localdata=True

    for n in options.newname:
        tx = t.split(t,':')
        taxid = options.taxonomy.addPreferedName(tx[0].strip(),tx[1])
        print "name : %8d\t->\t%s" % (taxid,options.taxonomy.getPreferedName(taxid))
             
    ecoTaxonomyWriter(options.ecodb,options.taxonomy,onlyLocal=True)

    