def printNestedList(data, indent=False, level=0):
	for item in data:
		if(isinstance(item, list)):
			printNestedList(item, indent, level+1)
		else:
			if indent:
				for tab in range(level):
					print('\t', end='')
			print(item)