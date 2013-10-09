def printline(the_list):
    for each_line in the_list:
        if isinstance(each_line,list):
            printline(each_line)
        else:
            print (each_line)
