'''This module opens a theatre script and prints it out nicely.'''

def write(script):
	"""Script should be a text document play.
	Use string quotes: 'my_play.txt'
	Should look like CHARACTER: LINE SPOKEN.
	The function rewrites it as MAN says: LINE SPOKEN."""
	
	try:
		data = open(script)
		
		for each_line in data:
			try:
				(role, line_spoken) = each_line.split(':')
				print(role, end = '')
				print(' says: ', end = '')
				print(line_spoken, end = '')
			except ValueError:
				pass
		
		data.close()
	
	except IOError:
		print('The file could not be opened.')

