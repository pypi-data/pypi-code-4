"""Show the different uses of Commandeer"""

import commandeer

def echo_command(*inp):
	"""Print all the words that were passed on the command line
	
	This is just a simple echo command.
	"""
	print(' '.join(inp))

if __name__ == '__main__':
	commandeer.cli()
