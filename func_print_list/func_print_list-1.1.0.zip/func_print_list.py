'''
Created on 2013-5-25

@author: shao

模块注释：
    此模块包含打印一个嵌套链表的方法
'''

def print_list(the_list,level=0):
    '''
        打印嵌套列表the_list
    :param the_list:
    :param level: 指定缩进的级别
    '''
    for item in the_list:
        if isinstance(item,list):
            print_list(item,level+1)
        else:
            for num in range(level):
                print("\t",end='')
            print(item)