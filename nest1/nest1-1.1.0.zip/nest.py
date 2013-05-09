"""this is a module whose function is to print nested ot simple list"""
"""A second argument called "level" is used to insert tab-stop when a nested list is encounterd"""
def givePrint(the_list,level=0):
    """the function will take a list as an arguemrnt and the 'if' will check
    the list is nested or not,if it is nested then recursion will be used"""
    for each_item in the_list:
        if isinstance(each_item,list):
            givePrint(each_item,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(each_item)
