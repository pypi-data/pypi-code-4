""" this function prints a list in al ist"""

def print_nest(the_list):
	for each_item in the_list:
		if isinstance (each_item):
			print_nest(each_item)
		else:
			print(each_item)
