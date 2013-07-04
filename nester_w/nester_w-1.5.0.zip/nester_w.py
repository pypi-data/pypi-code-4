"""This is my first module"""

import sys

def show(a_list, indent=False, space=0, out=sys.stdout):
    """递归输出所有列表项,'space'参数用于指定打印数据前的制表符数量,
       'indent'参数可设置是否使用缩进功能,默认为关闭状态,'out'参数
       设置数据输出的方式,默认为标准输出(屏幕)"""
    if isinstance(a_list, list):
        for item in a_list:
            show(item, indent, space+1, out)
    else:
        if indent:
            print("\t"*space, end='', file=out)
        print(a_list, file=out)

def sanitize(time_string):
    """将带'-'和':'格式字符串转换为时间格式"""
    if '-' in time_string:
        splitter = '-'
    elif ':' in time_string:
        splitter = ':'
    else:
        return time_string
    (mins, secs) = time_string.split(splitter)
    return(mins + "." + secs)
