''' This is the "nesty.py" module, it provides one funcioin called 
 print_lol() which prints out a list that may or may not include nested lists.'''

def print_lol (the_list):
  ''' This function takes a propositional argument "the list" which is a list in python that may content any data item. Each data item in the provided list is (recursively) printed on the screen on its own line. '''
  for elemt in the_list :
    if isinstance (elemt, list):
        print_lol(elemt)
    else:
        print elemt





