"""
My first make code. 2013-05-16.
This is a module of "study_nester.py"
This provides on function called print_list() which prints lists that may or may not include nested list.

ver. 1.2.0. add segment, input tap value
"""
def print_list(the_list, level=0):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_list(each_item, level+1)
		else:
			for tab_stop in range(level):
				print("\t", end='')
			print(each_item)
