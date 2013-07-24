'''This module will take a string of times and return the top three fastest.
It can be used for oganizing athlete data and tracking fitness. It 
requires a text file (.txt) with the list of times.
Please do not use , to separate minutes/seconds.
EXAMPLE: [2.22, 4.2, 3:50, 6-20, 2.44]'''

# First an empty list is created and populated by the time strings

athlete = []
user = input('Please input the name of your txt file: ')

def get_data(text):
    try:
        with open(text) as file:
            data = file.readline()
            return data.strip().split(',')
    except IOError as err:
        print('File error: ' + str(err))
        return(None)

athlete = get_data(user)

# The data is processed and formatted
# Duplicates are removed with 'set'

def sanitize(time):
    if '-' in time:
        splitter = '-'
    elif ':' in time:
        splitter = ':'
    else:
        return time
    
    (mins, secs) = time.split(splitter)
    return(mins + '.' + secs)

print('Your top three fastest times')
print()
print(sorted(set([sanitize(t) for t in athlete])) [0:3])
