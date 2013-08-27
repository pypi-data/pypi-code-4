""" This module contains some utility functions that you might be interested in.
It's my first module, so let me know if I get something wrong about Python
"""

def print_lol(the_list,identation=0):
    """ This function prints all items of a list in the standard output (console)
	It also prints items of nested items. It does recursively (which is always awesome). """
    for item in the_list:
        if isinstance(item,list):
            print_lol(item,identation+1)
        else:
            iden = ""
            if (identation != 0):                
                for n in range(identation):
                    iden += "\t"
            print(iden + str(item))
            

