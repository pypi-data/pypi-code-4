'''
Created on 2013-8-6

@author: lenovo
'''
def print_list(the_list):
    for item in the_list:
        if(isinstance(item, list)):
            print_list(item)
        else:
            print(item)