

def print_lol(s):
	for x in s:
		if isinstance(x, list):
			print_lol(x)
		else:
			print x
def suojn(s,level):
	for x in s:
		if isinstance(x, list):
			suojn(x,level+1)
		else:
			for t in range(level):
				print '\t',
			print x
		# print 
		
def get_lol(s,t):
	for x in s:
		if isinstance(x, list):
			get_lol(x,t)
		else:
			t.append(x)
	
t = []
s= ['a',1,3,4,5,[1,2,34,'4',[5,56,['33']]],12,32414,42354]
suojn(s,0)
# get_lol(s,t)
# print t