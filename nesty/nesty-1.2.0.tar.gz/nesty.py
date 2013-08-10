''' This is the "nesty.py" module, it provides one funcioin called 
 print_lol() which prints out a list that may or may not include nested lists.'''

def print_lol (the_list, indent = False,level=0):
  ''' This function takes a propositional argument "the list" which is a list in python that may content any data item, and two optional argument, "indent (boolean)", which specifies if indentation of nested list is required, and "level (int)" which specifies the level of indentation. Each data item in the provided list is (recursively) printed on the screen on its own line. '''
  for elemt in the_list :
    if isinstance (elemt,list):
        print_lol(elemt,indent,level+1)

    else:
        if indent:
          for tab_stop in range(level):
             print '\t',
        print elemt





