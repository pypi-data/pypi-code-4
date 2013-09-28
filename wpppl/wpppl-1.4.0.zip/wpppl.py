'''这是“wpppl.py”模块，提供了一个名为wpppl（）的函数，这个函数的作用是打印列表，其中有可能
包含或者不包含列表'''



def wpppl(the_list,indent=False,level=0):
    '''这个函数取一个位置参数，名为the_list，这可以使任何的python列表。所指定的列表中的每一个数据项
（递归地）输出到屏幕上，各数据项占一行。第二个参数indent是否打开缩进，默认是不打开。第三个参数是在遇到嵌套表格时插入制表符。'''
    for each in the_list:
        if isinstance(each,list):
            wpppl(each,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t",end='')
            print(each)
