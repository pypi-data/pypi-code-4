"""helloworld, this is my first python function, it is used to print lists!"""
def printlist(listname):
	for i in listname:
		if isinstance(i, list):
			"""you see, it is a recursion"""
			printlist(i)
		else:
			print(i)