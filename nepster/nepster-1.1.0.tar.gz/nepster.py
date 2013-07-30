#this is the nepster function in python which provide one function called 
#loop_funcn which prints list .

def loop_funcn(the_list,level):
# it takes the argument the_list , which is any python list 
#that does blah blah blah
	for each_item in the_list:
		if isinstance (each_item,list):
			loop_funcn(each_item,level+1)
		else:
			print(each_item)