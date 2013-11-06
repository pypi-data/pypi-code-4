from operator import itemgetter

#list to dict conversion 
lst = [('username', 'erob'), ('password', 'secret')]

data = dict(map(itemgetter(0,1), lst))
print data

