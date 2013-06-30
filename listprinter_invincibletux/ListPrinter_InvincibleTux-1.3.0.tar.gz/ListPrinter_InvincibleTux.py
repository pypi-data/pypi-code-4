def print_list(the_list, indent=False, level=0):
	for entry in the_list:
		if isinstance(entry, list):
			print_list(entry, indent, level + 1)
		else:
			if indent:			
				for num in range(level):
					print("   ", end='')
			print(entry)
			
