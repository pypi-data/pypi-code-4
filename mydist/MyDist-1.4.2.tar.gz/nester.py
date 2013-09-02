""" This module contains some utility functions that you might be interested in.
It's my first module, so let me know if I get something wrong about Python
"""

import sys

def print_lol(the_list,identation=0,ident=False,output=sys.stdout):
    """ This function prints all items of a list in the output (sys.stdout is default)
	It also prints items of nested items. It does recursively (which is always awesome). """
    for item in the_list:
        if isinstance(item,list):
            print_lol(item,identation+1,ident)
        else:
            iden = ""
            if (ident):                
                for n in range(identation):
                    iden += "\t"
            print >> output,(iden + str(item))
            

