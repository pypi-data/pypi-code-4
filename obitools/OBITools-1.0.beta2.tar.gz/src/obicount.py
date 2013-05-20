#!/usr/local/bin/python
'''
:py:mod:`obicount`: Counts the number of sequence records 
=========================================================

.. codeauthor:: Eric Coissac <eric.coissac@metabarcoding.org>

:py:mod:`obicount` counts the number of sequence records and/or the sum of the ``count`` attributes.

*Example:*

    .. code-block:: bash
        
        > obicount seq.fasta  

    Prints the number of sequence records contained in the ``seq.fasta`` 
    file and the sum of their ``count`` attributes.
'''

from obitools.options import getOptionManager
from obitools.format.options import addInOutputOption

def addCountOptions(optionManager):
    group=optionManager.add_option_group('Obicount specific options')
    group.add_option('-s','--sequence',
                             action="store_true", dest="sequence",
                             default=False,
                             help="Prints only the number of sequence records."
                             )
 
    group.add_option('-a','--all',
                             action="store_true", dest="all",
                             default=False,
                             help="Prints only the total count of sequence records (if a sequence has no `count` attribute, its default count is 1) (default: False)."
                             )


if __name__ == '__main__':
    optionParser = getOptionManager([addCountOptions,addInOutputOption], progdoc=__doc__)
    
    (options, entries) = optionParser()
    
    count1=0
    count2=0
    
    for s in entries:
        count1+=1
        if 'count' in s:
            count2+=s['count']
        else:
            count2+=1
            
    if options.all==options.sequence:
        print count1,count2
    elif options.all:
        print count2
    else:
        print count1
        