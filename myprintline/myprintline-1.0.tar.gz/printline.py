# -*- coding: utf-8 -*-
'''
    用来介绍模块，说明模块有什么功能
'''
import sys
def printline(the_list,num=0,indent=False,data=sys.stdout):
    '''参数介绍'''
    for each_line in the_list:
        if isinstance(each_line,list):
            printline(each_line,num+1,indent,data)
        else:
            if indent==True:    #写成 indent也可以       
                for x in range(num):
                    print("\t",end=',',file=data)
            print(each_line,file=data)

