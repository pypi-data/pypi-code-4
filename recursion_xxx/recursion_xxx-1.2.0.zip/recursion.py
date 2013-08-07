'''
Created on 2013-8-6

@author: lenovo
This is the "recursion.py" module and it provides one function called print_list()
which prints lists that may or may not include nested lists.
'''
def print_list(the_list, level=0):
    for item in the_list:
        if(isinstance(item, list)):
            print_list(item,level+1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(item)
