def print_lol(the_list,ident=False,level=0):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item,ident, level+1)
		else:
			if ident:
				for tab_stop in range(level):
					print("\t", end='')
			print(each_item)
