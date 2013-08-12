def print_lol(the_list, tab=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,tab+1)
        else:
            for i in range(tab):
                print('\t', end='')
            print(each_item)


