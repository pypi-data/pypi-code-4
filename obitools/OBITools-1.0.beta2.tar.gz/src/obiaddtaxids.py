#!/usr/local/bin/python
'''
:py:mod:`obiaddtaxids`: Adds taxids to sequence records using an ecopcr database
================================================================================

.. codeauthor:: Celine Mercier <celine.mercier@metabarcoding.org>

The :py:mod:`obiaddtaxids` command annotates sequence records with a taxid based on 
a taxon scientific name stored in the sequence record header.

Taxonomic information linking a taxid to a taxon scientific name is stored in a 
database formatted as an ecopcr database (see :doc:`obitaxonomy <obitaxonomy>`) or 
a NCBI taxdump (see NCBI ftp site).

The way to extract the taxon scientific name from the sequence record header can be
specified by two options:

    - By default, the sequence identifier is used. Underscore characters (``_``) are substituted
      by spaces before looking for the taxon scientific name into the taxonomic
      database.

    - If the input file is an :doc:`OBITools extended fasta format <../fasta>`, the ``-k`` option
      specifies the attribute containing the taxon scientific name.

    - If the input file is a fasta file imported from the UNITE or from the SILVA web sites,
      the ``-f`` option allows specifying this source and parsing correctly the associated 
      taxonomic information.
      
  
For each sequence record, :py:mod:`obiaddtaxids` tries to match the extracted taxon scientific name 
with those stored in the taxonomic database.

    - If a match is found, the sequence record is annotated with the corresponding ``taxid``.

Otherwise,
    
    - If the ``-g`` option is set and the taxon name is composed of two words and only the 
      first one is found in the taxonomic database at the 'genus' rank, :py:mod:`obiaddtaxids` 
      considers that it found the genus associated with this sequence record and it stores this 
      sequence record in the file specified by the ``-g`` option.
    
    - If the ``-u`` option is set and no taxonomic information is retrieved from the 
      scientific taxon name, the sequence record is stored in the file specified by the 
      ``-u`` option.

'''


import sys

from obitools.fasta import fastaIterator,formatFasta
from obitools.options import getOptionManager
from obitools.options.taxonomyfilter import addTaxonomyDBOptions
from obitools.options.taxonomyfilter import loadTaxonomyDatabase
from obitools.format.genericparser import genericEntryIteratorGenerator
from obitools import NucSequence


def addObiaddtaxidsOptions(optionManager):
    
    optionManager.add_option('-g','--genus_found',
                             action="store", dest="genus_found",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="(not with UNITE databases) file used to store sequences with the genus found.")

    optionManager.add_option('-u','--unidentified',
                             action="store", dest="unidentified",
                             metavar="<FILENAME>",
                             type="string",
                             default=None,
                             help="file used to store completely unidentified sequences.")

    optionManager.add_option('-s','--dirty',
                             action='store', dest="dirty",
                             metavar="<FILENAME>",
                             type="str",
                             default=None,
                             help="(not with UNITE databases) if chosen, ALL the words in the name used to identify the sequences will be searched"
                                  " when neither the exact name nor the genus have been found."
                                  " Only use if the sequences in your database are badly named with useless words or numbers"
                                  " in the name etc."
                                  " The sequences identified this way will be written in <FILENAME>.")
    
    optionManager.add_option('-f','--format',
                             action="store", dest="db_type",
                             metavar="<FORMAT>",
                             type="string",
                             default='raw',
                             help="type of the database with the taxa to be added. Possibilities : 'raw', 'UNITE' or 'SILVA'."
                             " Default : raw.")
    
    optionManager.add_option('-k','--key-name',
                             action="store", dest="tagname",
                             metavar="<KEYNAME>",
                             type="string",
                             default='',
                             help="name of the key attribute containing the taxon name in databases of 'raw' type. Default : the taxon name is the id "
                             "of the sequence. The taxon name MUST have '_' between the words of the name when it's the id, and "
                             "CAN be of this form when it's in a field.")

    optionManager.add_option('-a','--restricting_ancestor',
                             action="store", dest="res_anc",
                             type="str",
                             metavar="<ANCESTOR>",
                             default='',
                             help="can be a word or a taxid (number). Enables to restrict the search of taxids under a "
                                  "specified ancestor. If it's a word, it's the field containing the ancestor's taxid "
                                  "in each sequence's header (can be different for each sequence). If it's a number, "
                                  "it's the taxid of the ancestor (in which case it's the same for all the sequences)")



def numberInStr(s) :
    containsNumber = False
    for c in s :
        if c.isdigit() :
            containsNumber = True
    return containsNumber


def UNITEIterator(f):
    
    fastaEntryIterator = genericEntryIteratorGenerator(startEntry='>')
    for entry in fastaEntryIterator(f) :
        all = entry.split('\n')
        header = all[0]
        fields = header.split('|')
        id = fields[0][1:]
        seq = all[1]
        s = NucSequence(id, seq)
        s['ISDN_species_name'] = fields[1]
        s['UNITE_species_name'] = fields[3]
        path1 = fields[2].replace(';', ',')
        path2 = fields[4].replace(';', ',')
        s['ISDN_path'] = path1
        s['UNITE_path'] = path2
        yield s


def SILVAIterator(f, tax):
    
    fastaEntryIterator = genericEntryIteratorGenerator(startEntry='>')
    for entry in fastaEntryIterator(f) :
        all = entry.split('\n')
        header = all[0]
        fields = header.split(' | ')
        id = fields[0][1:]
        seq = all[1]
        s = NucSequence(id, seq)
        
        if (
            '(' in fields[1] 
            and len(fields[1].split('(')[1][:-1]) > 2 
            and ')' not in fields[1].split('(')[1][:-1] 
            and not numberInStr(fields[1].split('(')[1][:-1])
            ) :
            species_name = fields[1].split('(')[0][:-1]
            other_name = fields[1].split('(')[1][:-1]
            
            ancestor = None
            notAnAncestor = False
            
            if (len(other_name.split(' ')) == 1 and other_name[0].isupper()):
                
                try:
                    ancestor = tax.findTaxonByName(other_name)
                except KeyError :
                    notAnAncestor = True
            
            if (ancestor == None and notAnAncestor == False):
                s['common_name'] = other_name
                s['original_silva_name'] = fields[1]
                s['species_name'] = species_name
            
            elif (ancestor != None and notAnAncestor == False) :
                s['ancestor_name'] = other_name
                s['ancestor'] = ancestor[0]
                s['original_silva_name'] = fields[1]
                s['species_name'] = species_name
                
            elif notAnAncestor == True :
                s['species_name'] = fields[1]
                        
        else :
            s['species_name'] = fields[1]
        
        yield s

    
def dirtyLookForSimilarNames(name, tax, ancestor):
    
    similar_name = ''
    taxid = None
    
    try :
        t = tax.findTaxonByName(name)
        taxid = t[0]
        similar_name = t[3]
    
    except KeyError :
        taxid = None
        
    if ancestor != None and not tax.isAncestor(ancestor, taxid) :
        taxid = None
    
    return similar_name, taxid
    

def getGenusTaxid(tax, species_name, ancestor):
    genus_sp = species_name.split(' ')
    genus_taxid = getTaxid(tax, genus_sp[0], ancestor)
    if tax.getRank(genus_taxid) != 'genus' :
        raise KeyError()
    return genus_taxid


def getTaxid(tax, name, ancestor):

    taxid = tax.findTaxonByName(name)[0]
    if ancestor != None and not tax.isAncestor(ancestor, taxid) :
        raise KeyError()
    
    return taxid


def get_species_name(s, options) :
    
    species_name = None
    if options.tagname == '' or options.tagname in s :
        if options.tagname == '' :
            species_name = s.id
        else :
            species_name = s[options.tagname]
                
        if "_" in species_name :
            species_name = species_name.replace('_', ' ')
          
        if len(species_name.split(' ')) == 2 and (species_name.split(' ')[1] == 'sp' or species_name.split(' ')[1] == 'sp.' or species_name.split(' ')[1] == 'unknown') :
            species_name = species_name.split(' ')[0]
          
        if options.tagname == '' :
            s['species_name'] = species_name
    
    return species_name


def getVaguelySimilarNames(species_name, tax, restricting_ancestor) :
    
    kindOfFound = False              
    uselessWords = ['sp', 'sp.', 'fungus', 'fungal', 'unknown', 'strain', 'associated', 'uncultured']
    for word in species_name.split(' ') :
        if word not in uselessWords :
            similar_name, taxid = dirtyLookForSimilarNames(word, tax, restricting_ancestor)
            if taxid != None :
                if len(similar_name) > len(s['species_name']) or kindOfFound == False :
                    s['species_name'] = similar_name
                    kindOfFound = True
    return kindOfFound


def openFiles(options) :
    
    if options.unidentified is not None:
        options.unidentified=open(options.unidentified,'w')
    
    if options.genus_found is not None:
        options.genus_found=open(options.genus_found,'w')
        
    if options.dirty is not None:
        options.dirty = open(options.dirty, 'w')


################################################################################################

if __name__=='__main__':

    optionParser = getOptionManager([addObiaddtaxidsOptions, addTaxonomyDBOptions], progdoc=__doc__)
    
    (options,entries) = optionParser()
    
    tax=loadTaxonomyDatabase(options)
    
    if options.db_type == 'raw' :
        entryIterator = fastaIterator
        entries = entryIterator(entries)
    elif options.db_type == 'UNITE' :
        entryIterator = UNITEIterator
        entries = entryIterator(entries)
    elif options.db_type == 'SILVA' :
        entryIterator = SILVAIterator
        entries = entryIterator(entries, tax)
        options.tagname = 'species_name'

    openFiles(options)
    
    if (options.db_type == 'raw') or (options.db_type == 'SILVA') :
        
        if options.res_anc == '' :
            restricting_ancestor = None
        elif options.res_anc.isdigit() :
            restricting_ancestor = int(options.res_anc)
        
        for s in entries:
            
            if options.res_anc != '' and not options.res_anc.isdigit():
                restricting_ancestor = int(s[options.res_anc])
            
            species_name = get_species_name(s, options)
            
            if species_name != None :    
                try:
                    taxid = getTaxid(tax, species_name, restricting_ancestor)
                    s['taxid'] = taxid
                    print formatFasta(s)
                
                except KeyError:
                    
                    genusFound = False
                    if options.genus_found is not None and len(species_name.split(' ')) >= 2 :
                        try:
                            genusTaxid = getGenusTaxid(tax, species_name, restricting_ancestor)
                            print>>options.genus_found, formatFasta(s)
                            genusFound = True
                        except KeyError :
                            pass
                    
                    kindOfFound = False
                    if options.dirty is not None and not genusFound :
                        kindOfFound = getVaguelySimilarNames(species_name, tax, restricting_ancestor)
                        if kindOfFound == True :
                            print>>options.dirty, formatFasta(s)
                    
                    if options.unidentified is not None and not genusFound and not kindOfFound :
                        print>>options.unidentified,formatFasta(s)


    elif options.db_type == 'UNITE' :
        restricting_ancestor = tax.findTaxonByName('Fungi')[0]
        for s in entries :
          
            try:
                species_name = s["UNITE_species_name"]
                taxid = getTaxid(tax, species_name, restricting_ancestor)
                s['taxid']=taxid
                s["species_name"] = species_name
                print formatFasta(s)
            
            except KeyError:
                try:
                    species_name = s["ISDN_species_name"]
                    print species_name
                    taxid = getTaxid(tax, species_name, restricting_ancestor)
                    s['taxid']=taxid
                    s["species_name"] = species_name
                    print formatFasta(s)
                
                except KeyError:
                    
                    if s["UNITE_species_name"] != "-" and s["UNITE_species_name"] != "" :
                        s["species_name"] = s["UNITE_species_name"]
                        chosen = 'unite'
                    
                    elif s["ISDN_species_name"] != "-" and s["ISDN_species_name"] != "" :
                        s["species_name"] = s["ISDN_species_name"]
                        chosen = 'isdn'
                    
                    else :
                        if s["UNITE_path"] != "-" and s["UNITE_path"] != "" :
                            chosen = 'unite'
                            s["species_name"] = (s["UNITE_path"].split(', '))[-1]
                        
                        elif s["ISDN_path"] != "-" and s["ISDN_path"] != "" :
                            chosen = 'isdn'
                            s["species_name"] = (s["ISDN_path"].split(', '))[-1]
                        
                        else : 
                            print>>sys.stderr, "\n\nwarning : sequence without any identification at all\n\n"
                                        
                    if chosen == 'unite' :
                            s['path'] = s["UNITE_path"]
                    else :
                            s['path'] = s["ISDN_path"]
                    
                    if options.unidentified is not None :
                        print>>options.unidentified,formatFasta(s)
                             
                                