

movies=["大上海",2013,"周润发",["黄晓明",["赵薇","陈坤"]]]

def print_lol(the_list,indent=False,level=0):
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab in range(level):
                    print("\t",end='')
            print(each_item)


print_lol(movies,True)

