#! /usr/bin/python
#-*-coding:utf-8-*-
"""这个模块用来处理嵌套列表的输出"""

def print_lol (the_list):
    """递归打印列表中的所有元素，the_list可以是普通列表也可以是嵌套列表"""
    for i in the_list:
        if isinstance (i,list):
            print_lol (i)
        else:
            print (i*2)
