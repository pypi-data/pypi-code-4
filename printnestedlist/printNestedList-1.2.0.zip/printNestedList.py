def printNestedList(data, level=0):
	for item in data:
		if(isinstance(item, list)):
			printNestedList(item, level+1)
		else:
			for tab in range(level):
				print('\t', end='')
			print(item)