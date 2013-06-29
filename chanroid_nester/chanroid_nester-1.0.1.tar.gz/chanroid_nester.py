# -*- coding:utf-8 -*-
def print_list(array, numOfTabs):
	# array - 출력할 배열, numOfTabs - 들여쓰기 할 탭 수
	for item in array:
		if (isinstance(item, list)):
			print_list(item, numOfTabs+1)
		else:
			for tab in range(numOfTabs):
				print("\t", end='')
			print(item)