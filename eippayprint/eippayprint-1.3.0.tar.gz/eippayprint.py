"""This is the "nester.py" module and it provides one function called print_lol() which prints lists that may or may not include nested lists."""
def print_list(the_list,ident=False,level=0):
	"""this function takes one positional argument called "the_list",which is any python list (of - possible -nested lists). Each data item in the provided list is (recuraively) printed to the screen on it'2 own line."""
	if isinstance(the_list,list):
		for each_item in the_list:
			print_list(each_item,ident,level+1)
	else:
		if ident:
			for tab_stop in range(level):
				print("\t",end='')
			print(the_list)
		else:
			print(the_list)
