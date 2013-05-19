#movies=["the holy grail",1975,"terry jones & terry gilliam",91,["graham chapman",["michael palin","john cleese","terry gilliam","eric idle","terry jones"]]]
""" definition a function for iterate print movies"""
def print_movies(the_list,level=0):
	for each_item in the_list:
		if isinstance(each_item,list):
		     print_movies(each_item,level+1)
		else:
		     for tab_stop in range(level):
			     print("\t",end='')
		     print(each_item)
