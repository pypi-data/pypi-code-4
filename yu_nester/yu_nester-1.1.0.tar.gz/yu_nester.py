def printList(the_list, level = 0):
    # simple test from Head First Python
    # print all the nested list

    for each_item in the_list:
        if isinstance(each_item, list):
            printList(each_item, level + 1)
        else:
            for tab_stop in range(level):
                print("\t", end = '')
            print(each_item)
