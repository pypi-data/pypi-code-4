'''
Created on 2013��10��1��

@author: 张静波 myplaylife@gmail.com
'''

my_list = ["zhangjingbo", ["play", "life"], "my", "haha", ["hei", "ha", ["ho", "mama", "miya"]]]

def print_lol(the_list, level):
    for s in the_list:
        if isinstance(s, list):
            print_lol(s, level + 1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(s)
        
        
print_lol(my_list, 0)