'''这个module用来打印一个列表中的内容，如果有嵌套的列表，nester会深入进去打印'''
def nester(x_or_list):
	'''这个函数只需要一个参数x_or_list，如果x不是列表就直接打印，如果是列表，会继续深入到列表中的项直到遇到一个非列表，再将这个非列表项打印出来'''
	if isinstance(x_or_list,list):
		for item in x_or_list:
			nester(item)
	else:
		print(x_or_list)