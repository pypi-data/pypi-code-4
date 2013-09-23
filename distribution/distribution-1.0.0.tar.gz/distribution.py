#!-*-coding:utf-8-*-
#!/usr/bin/python

def circle_print(some_list):
	for eachItem in some_list:
		if isinstance(eachItem,list):
			circle_print(eachItem)
		else:
			print eachItem
