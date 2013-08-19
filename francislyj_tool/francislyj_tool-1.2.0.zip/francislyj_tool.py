def printlist(l, level=0):
    for i in l:
        if isinstance(i, list):
            printlist(i, level + 1)
        else:
        	for tab in range(level):
        		print("\t", end="")
        	print(i)