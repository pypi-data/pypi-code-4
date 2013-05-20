#!/usr/local/bin/python
'''
:py:mod:`obiuniq`: Groups and dereplicates sequences  
====================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

The :py:mod:`obiuniq` command is in some way analog to the standard Unix ``uniq -c`` command.

Instead of working text line by text line as the standard Unix tool, the processing is done on 
sequence records. 

A sequence record is a :doc:`complex object <../fasta>` composed of an identifier, a set of 
attributes (``key=value``), a definition, and the sequence itself. 

The :py:mod:`obiuniq` command groups together sequence records. Then, for each group, a sequence 
record is printed.

A group is defined by the sequence and optionally by the values of a set of attributes 
specified with the ``-c`` option.

As the identifier, the set of attributes (``key=value``) and the definition of the sequence 
records that are grouped together may be different, two options (``-m`` and ``-i``) 
allow refining how these parts of the records are reported.

    - By default, only attributes with identical values 
      within a group of sequence records are kept.

    - A ``count`` attribute is set to the total number of sequence records for each group.
      
    - For each attribute specified by the ``-m`` option, a new attribute whose key is prefixed 
      by ``merged_`` is created. These new attributes contain the number of times each value
      occurs within the group of sequence records. 
    
:py:mod:`obiuniq` and taxonomic information
-------------------------------------------
    
When a taxonomy is loaded (``-d`` or ``-t`` options), the ``merged_taxid`` 
attribute is created and records the number of times each taxid has been found in the 
group (it may be empty if no sequence record has a ``taxid`` attribute in the group). 
In addition, a set of taxonomy-related attributes are generated for each group having at 
least one sequence record with a ``taxid`` attribute. The ``taxid`` attribute of the sequence
group is set to the *Last Common Ancestor* of the taxids of the group. All other taxonomy-related 
attributes created (``species``, ``genus``, ``family``, ``species_name``, ``genus_name``, 
``family_name``, ``rank``, ``scientific_name``) give information on the *Last Common Ancestor*.
  
'''


from obitools.format.options import addInputFormatOption
from obitools.fasta import formatFasta
from obitools.utils.bioseq import uniqSequence,uniqPrefixSequence
from obitools.options import getOptionManager
from obitools.options.taxonomyfilter import addTaxonomyDBOptions
from obitools.options.taxonomyfilter import loadTaxonomyDatabase

def addUniqOptions(optionManager):
    group = optionManager.add_option_group('Obiuniq specific options')
    group.add_option('-m','--merge',
                             action="append", dest="merge",
                             metavar="<TAG NAME>",
                             type="string",
                             default=[],
                             help="Attributes to merge")

    group.add_option('-i','--merge-ids',
                             action="store_true", dest="mergeids",
                             default=False,
                             help="Add the merged id data to output")
   
    group.add_option('-c','--category-attribute',
                             action="append", dest="categories",
                             metavar="<Attribute Name>",
                             default=[],
                             help="Add one attribute to the list of attributes "
                             "used to group sequences before dereplication "
                             "(option can be used several times)")

    group.add_option('-p','--prefix',
                             action="store_true", dest="prefix",
                             default=False,
                             help="Dereplication is done based on prefix matching: "
                                  "(i) The shortest sequence of each group is a prefix "
                                  "of any sequence of its group (ii) Two shortest "
                                  "sequences of any couple of groups are not the"
                                  "prefix of the other one")
    

if __name__=='__main__':

#    root.setLevel(DEBUG)

    optionParser = getOptionManager([addUniqOptions,addTaxonomyDBOptions,addInputFormatOption],progdoc=__doc__)
    
    (options, entries) = optionParser()

    taxonomy=loadTaxonomyDatabase(options)
    
    if options.prefix:
        usm = uniqPrefixSequence
    else:
        usm= uniqSequence

    uniqSeq=usm(entries,taxonomy,options.merge,options.mergeids,options.categories)
 
    for seq in uniqSeq:         
        print formatFasta(seq) 
