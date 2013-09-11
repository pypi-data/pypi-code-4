import commandeer

def ls_command(*varargs):
	print('\n'.join(varargs))
	
if __name__ == '__main__':
	commandeer.cli()