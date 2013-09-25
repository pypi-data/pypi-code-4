#Reading a file
def readfile(filename):
	try:
		file=open(filename)
		i=nc=nw=0
		print "File Contents:\n----------------"
		for line in file:
			nc=len(line)+nc
			print line,
			nw=len(line.split(" "))+nw
			i=i+1
		print "\n---------------\nNumber Of lines in File:",i
		print "Number Of words in File:",nw
		print "Number Of Charcters in File:",nc
	except:
		print("Could not open file")