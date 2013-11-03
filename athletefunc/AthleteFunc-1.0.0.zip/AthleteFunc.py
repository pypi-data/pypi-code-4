def sanitize(time_string):
    if '-' in time_stirng:
        splitter="-"
        (mins,secs)=time_string.split(splitter)
    elif ':' in time_string:
        splitter=":"
        (mins,secs)=time_string.split(splitter)
    return(mins+'.'+secs)
