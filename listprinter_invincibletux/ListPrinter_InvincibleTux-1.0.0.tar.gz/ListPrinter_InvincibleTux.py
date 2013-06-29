def print_list(the_list):
	for entry in the_list:
		if isinstance(entry, list):
			print_list(entry)
		else:
			print(entry)
