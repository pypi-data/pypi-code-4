__author__ = 'benqing.shen'

# print('Hello')


def print_lol(the_list):
    """
    print list of list, recursion function
    """
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print item

