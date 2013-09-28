'''这是“wpppl.py”模块，提供了一个名为wpppl（）的函数，这个函数的作用是打印列表，其中有可能
包含或者不包含列表'''



def wpppl(the_list):
    '''这个函数取一个位置参数，名为the_list，这可以使任何的python列表。所指定的列表中的每一个数据项
（递归地）输出到屏幕上，各数据项占一行。'''
    for each in the_list:
        if isinstance(each,list):
            wpppl(each)
        else:
            print(each)
