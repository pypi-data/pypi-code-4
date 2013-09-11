import commandeer

# this function will be available as command 'test'
def test_command():
	print("test")
	
# this function will be available as command 'echo'
def text_command():
	print("echo")

# this function will be available as command 'class', i.e. a reserved word in python
def class_command():
	print("class")

# this function will not be available
def some_other_function():
	print("will not be reachable from the command line")
	
if __name__ == '__main__':
	commandeer.cli()