def List_spliter(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            List_spliter(each_item)
        else:
            print(each_item)
