def sanitize(time_string):
    if '-' in time_string:
        splitter="-"
    elif ':' in time_string:
        splitter=":"
    else:
        return(time_string)
    (mins,secs)=time_string.split(splitter)
    return(mins+'.'+secs)
def get_coach_data(filename):
    try:
        with open(filename) as file:
            data=file.readline()
            return(data.strip().split(','))
    except IOError as err:
        print('IOError: '+err)
        return(None)
        
