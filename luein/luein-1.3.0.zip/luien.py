"""test module for upload&share."""

def printItemsOfList(targetList, indent=False, level=0):
	for item in targetList:
		if isinstance(item, list):
			printItemsOfList(item, indent, level + 1)
		else:
			if indent:
				for tapCount in range(level):
					print("\t", end = '')

			print(item)