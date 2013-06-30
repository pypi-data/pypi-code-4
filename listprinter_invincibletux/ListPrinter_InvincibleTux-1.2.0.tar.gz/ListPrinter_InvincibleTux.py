def print_list(the_list, level=0):
	for entry in the_list:
		if isinstance(entry, list):
			print_list(entry, level + 1)
		else:
			for num in range(level):
				print("   ", end='')
			print(entry)
			
