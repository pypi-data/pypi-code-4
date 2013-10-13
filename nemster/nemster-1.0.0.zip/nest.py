"""this is a function
"""
def repeat(haha):
	for enen in haha:
		if isinstance(enen,list):
			repeat(enen)
		else:
			print (enen)
