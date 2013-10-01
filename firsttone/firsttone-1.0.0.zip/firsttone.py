def firsttone(listname):
	for d in listname:
		if isinstance(d,list):
			firsttone(d)
		else:
			print(d)