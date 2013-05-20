#!/usr/local/bin/python
'''
:py:mod:`obiconvert`: Converts sequence files to different output formats
=========================================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obiconvert` converts sequence files to different output formats.
:doc:`See the documentation for more details on the different formats. <../formats>`

Input files can be in :

    - fasta format
    - *extended OBITools fasta* format
    - *sanger fastq* format
    - *solexa fastq* format
    - ecopcr format
    - ecopcr database format
    - genbank format
    - embl format

:py:mod:`obiconvert` converts those files to the :

    - *extended OBITools fasta* format
    - *sanger fastq* format
    - ecopcr database format
    
If no file name is specified, data is read from standard input. 

'''
 
from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption, sequenceWriterGenerator
from obitools.ecopcr.options import addTaxonomyDBOptions


if __name__ == '__main__':
    
    optionParser = getOptionManager([addInOutputOption,addTaxonomyDBOptions])
                                    
    (options, entries) = optionParser()
    writer = sequenceWriterGenerator(options)
       
    for entry in entries:
        writer(entry)
