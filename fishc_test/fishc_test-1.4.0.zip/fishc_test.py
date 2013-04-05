"""This is the "nester.py" module and it provides one function called print_lol()
   which prints lists that may or may not include nested lists."""
import sys
   
def print_lol(the_list, indent=False, level=0, file=sys.stdout):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item, indent, level+1, file)
		else:
			if indent:
				for tab_stop in range(level):
					print("\t", end='')
			print(each_item)
