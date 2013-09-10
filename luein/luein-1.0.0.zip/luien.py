"""test module for upload&share."""

def printItemsOfList(targetList):
	for item in targetList:
		if isinstance(item, list):
			printItemsOfList(item)
		else:
			print(item)