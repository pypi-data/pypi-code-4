'''movies = ["The Holy Grail", 1972, "Terry Jones & Terry Gilliam", 91,["Graham Chapman", ["Machael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]'''

def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)

'''print_lol(movies)'''
