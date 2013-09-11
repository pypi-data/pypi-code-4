import commandeer

def alias_command():
	pass

# add your aliases directly to the command function
alias_command.aliases = 'echo', 'trythis'

# WRONG example:
alias_command.aliases = 'echo'      # would lead to aliases 'e', 'c', 'h' and 'o'

# make sure that they are iterable, so if you have only one, don't forget the comma at the end!
alias_command.aliases = 'echo', 

