"""This is a sample script that shows two commands and how to call them from Commandeer."""

import commandeer
import datetime

def log_command(logcode, logmessage, timestamp=True, indent=0):
	"""Outputs the input, with an optional timestamp and some indenting.
	
	All of the input arguments are simply output on the standard out. If you specify indenting,
	the output will be prepended by that number of spaces. If you set timestamp to True, the
	output will be prepended by '[timestamp]'.
	@param logcode    The topic or code that this log will be added to.
	@param logmessage The message that will get logged
	@param timestamp  Add a timestamp to the output. A real timestamp.
	@param indent     The number of spaces the output should be indented by.
	"""
	echo_str = "[{}] {}".format(logcode, logmessage)
	if timestamp:
		echo_str = "[{}] {}".format(str(datetime.datetime.now()), echo_str)
	echo_str = " " * indent + echo_str
	print(echo_str)
	
if __name__ == '__main__':
	commandeer.cli()