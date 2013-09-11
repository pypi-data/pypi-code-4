import commandeer

def name_command(name, feeling):
	print("my name is {} and I am feeling {}".format(name, feeling))
	
if __name__ == '__main__':
	commandeer.cli()