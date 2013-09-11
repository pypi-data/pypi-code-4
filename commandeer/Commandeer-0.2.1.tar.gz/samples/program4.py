"""Show the different uses of Commandeer"""

import commandeer

def info_command(extrainfo=False, showdate=True, name='myself', age=30):
	"""Print some program information
	
	At the moment, this is pretty empty, but we will expand upon that in the future!
	@param extrainfo Enable extra information.
	@param name The name we inform about, part of the extra information.
	@param age The age of the person we inform about, part of the extra information.
	\param showdate Show a timestamp at the bottom of the ouput.
	"""
	print("This is my advanced info function")
	if extrainfo:
		print("Extra info was requested. The extra info is:")
		print("I am talking to {}, who is {} years old". format(name, age))
	if showdate:
		from datetime import datetime
		print(datetime.now())

if __name__ == '__main__':
	commandeer.cli()
