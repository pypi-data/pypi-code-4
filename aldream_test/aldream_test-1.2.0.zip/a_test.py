def print_lol(the_list, indent=False, tab=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item, indent, tab+1)
        else:
            if indent:
                for i in range(tab):
                    print('\t', end='')
            print(each_item)


