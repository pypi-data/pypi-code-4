"""This is a sample script that shows two commands and how to call them from Commandeer."""

import commandeer
import datetime

def func_command(argument1, argument2):
	"""A functional command: adding
	
	This command works by simply outputting its parameter."""
	try:
		a = float(argument1)
		b = float(argument2)
	except ValueError:
		print("Could not convert arguments to numbers. Please make sure they are in the right format!")
		return
	print(a+b)
func_command.aliases = 'add', 	
	
def log_command(logcode, *input, timestamp=True, indent=0):
	"""Outputs the input, with an optional timestamp and some indenting.
	
	All of the input arguments are simply output on the standard out. If you specify indenting,
	the output will be prepended by that number of spaces. If you set timestamp to True, the
	output will be prepended by '[timestamp] ' for fun.
	@param logcode The topic or code that this log will be added to.
	\param timestamp Add a timestamp to the output. A real timestamp.
	\param indent The number of spaces the output should be indented by.
	"""
	echo_str = "[{}] {}".format(logcode, ' '.join(input))
	if timestamp:
		echo_str = "[{}] {}".format(str(datetime.datetime.now()), echo_str)
	echo_str = " " * indent + echo_str
	print(echo_str)
	
if __name__ == '__main__':
	commandeer.cli()