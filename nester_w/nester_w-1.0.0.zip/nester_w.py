"""This is my first module"""

def show(a_list):
    """递归输出所有列表项"""
    if isinstance(a_list, list):
        for item in a_list:
            show(item)
    else:
        print(a_list)
