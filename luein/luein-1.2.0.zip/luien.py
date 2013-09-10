"""test module for upload&share."""

def printItemsOfList(targetList, level=0):
	for item in targetList:
		if isinstance(item, list):
			printItemsOfList(item, level + 1)
		else:
			for tapCount in range(level):
				print("\t", end = '')

			print(item)