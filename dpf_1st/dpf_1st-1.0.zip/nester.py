"""
打印列表
"""
def list_print(the_list):
    for each_item in the_list:
        if isinstance(each_item,list):
            list_print(each_item)
        else:
            print(each_item);

           
