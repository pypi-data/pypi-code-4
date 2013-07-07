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

def openfile(filename, splitter=","):
    """第一个参数'filename'为文件名,第二个
       参数'splitter'为分隔条件,默认按','
       逗号分隔,返回处理过列表后的字典"""
    try:
        with open(filename) as file:
            data = file.readline()
        a_list = data.strip().split(splitter)
        return({"name": a_list.pop(0), "birthday": a_list.pop(0), "time": str(sorted(set([sanitize(item) for item in a_list]))[0:3])})
    except IOError as err:
        print("Open file error:", err)
