'''
Caution: The API of this module have been changed
This module can be used to print a nested list and add serveral tab in front of the item
'''
def prnt(x_or_list,indent = -1):
	'''
	This function need two argument:
	The first argument is the list you want to print.
	The second represents that how many tab you want to be printed at the of the most outer item in the list
	'''

	if isinstance(x_or_list,list):
		indent = indent + 1
		for item in x_or_list:
			prnt(item,indent)
	else:
		print('\t' * indent,x_or_list)
		indent = 0