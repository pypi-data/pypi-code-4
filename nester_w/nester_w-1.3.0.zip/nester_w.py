"""This is my first module"""

def show(a_list, indent=False, space=0):
    """递归输出所有列表项,'space'参数用于指定打印数据前的制表符数量,
       indent参数可设置是否使用缩进功能,默认为关闭状态"""
    if isinstance(a_list, list):
        for item in a_list:
            show(item, indent, space+1)
    else:
        if indent:
            print("\t"*space, end='')
        print(a_list)
