def multiply_elements(list_or_string):
#This Function Multiplies numbers in a list or a String & soon Tuples !!
	ii = list_or_string
	try :
		ccc = 0;mm = 0;qq = 1
		if isinstance(ii,tuple):
			print("Lists and Strings are only accepted .... ")
			ccc = 1
		else:
			if isinstance(ii,list):
				for each in ii:
					eee = int(each)
					qq *= eee
			else:
				for each in ii:
					each = ii.strip().split(',')
					for eee in each:
						eee = int(each[mm])
						qq *= eee
						mm += 1
	except IndexError:
		pass
	finally:
		mm = 0
		if ccc == 0:
			return int(qq)