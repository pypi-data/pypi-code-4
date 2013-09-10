"""test module for upload&share."""

def printItemsOfList(targetList, level):
	for item in targetList:
		if isinstance(item, list):
			printItemsOfList(item)
		else:
			for tapCount in range(level):
				print("\t", end=")
			print(item)