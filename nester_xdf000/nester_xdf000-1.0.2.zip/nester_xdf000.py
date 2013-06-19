def pp_evething(the_list,level):
	for each_item in the_list:
                if isinstance(each_item,list):
                        pp_evething(each_item, level+1)
                else:
                        for tab_stop in range(level):
                                print("|----", end='')
                        print(each_item)
