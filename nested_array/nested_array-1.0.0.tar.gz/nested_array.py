#Python

def print_nested_array(array):
	for item in array:
		if isinstance(item, list):
			print_nested_array(item)
		else:
			print(item)
