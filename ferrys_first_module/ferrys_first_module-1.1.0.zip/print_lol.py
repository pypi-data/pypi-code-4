'''
Created on 2013��10��1��

@author: 张静波 myplaylife@gmail.com
'''

my_list = ["zhangjingbo", ["play", "life"], "my", "haha", ["hei", "ha", ["ho", "mama", "miya"]]]

def print_lol(the_list, indent=False, level=0):
    for s in the_list:
        if isinstance(s, list):
            print_lol(s, indent, level + 1)
        else:
            if indent:
                print("\t" * level, end='')
            print(s)
        
        
print_lol(my_list)