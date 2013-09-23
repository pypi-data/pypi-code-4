def printNestedList(data):
	for item in data:
		if(isinstance(item, list)):
			printNestedList(item)
		else:
			print(item)