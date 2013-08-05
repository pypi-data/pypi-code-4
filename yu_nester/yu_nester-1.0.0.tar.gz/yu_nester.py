def printList(the_list):
    # simple test from Head First Python
    # print all the nested list

    for each_item in the_list:
        if isinstance(each_item, list):
            printList(each_item)
        else:
            print(each_item)
