#!/usr/bin/env python3
"""This is the "print_lol.py" module and it provides a function called print_lol()
   which prints lists that may or may not include nested lists. """

def print_lol(list_item, indent = False, level = 0):
    """This function takes one positionall argument called "list_item", which
       is any Python list ( of - possibly - nested lists). Each data item in the
       provided list is (recursively) printed to the screen on its own line"""
    for each_item in list_item:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level + 1)
        else:
            if indent:
                for tab_stop in range(level):
                    print('\t', end='')
            print(each_item)

if __name__ == "__main__":
    list_item = [1, 2, [3, 4], [5, [6, 7]]]
    print_lol(list_item)
