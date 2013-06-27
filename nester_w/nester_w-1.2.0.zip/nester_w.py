"""This is my first module"""

def show(a_list, space=0):
    """递归输出所有列表项,'space'参数用于指定打印数据前的制表符数量"""
    if isinstance(a_list, list):
        for item in a_list:
            show(item, space+1)
    else:
        for s in range(space):
            print("\t", end='')
        print(a_list)
