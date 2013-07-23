def imLista (theList, level):
	for item in theList:
		if isinstance(item,list):
			imLista(item,level+1)
		else:
			for eachTab in range(level):
				print("\t", end="")
			print(item)
