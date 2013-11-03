def sanitize(time_string):
    if '-' in time_string:
        splitter="-"
    elif ':' in time_string:
        splitter=":"
    (mins,secs)=time_string.split(splitter)
    return(mins+'.'+secs)
