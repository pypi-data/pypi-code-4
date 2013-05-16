"""
My first make code. 2013-05-16.
This is a module of "study_nester.py"
This provides on function called print_list() which prints lists that may or may not include nested list.
"""
def print_list(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_list(each_item)
		else:
			print(each_item)
