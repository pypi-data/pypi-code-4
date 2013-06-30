def print_list(the_list, level):
	for entry in the_list:
		if isinstance(entry, list):
			print_list(entry, level + 1)
		else:
			for num in range(level):
				print("   ", end='')
			print(entry)
			
