
import itertools as it
import operator as op


def tab_separator(line):
    """Key-Value extraction function for tab-separated key-value lines
    """
    return line.strip().split('\t', 1)

def smap(mapper, lines, kvfunc=tab_separator):
    """Stream map: applies mapper to each line in input stream
    reducer function to the whole list of values.
    
     lines          - generator of key-value lines
     reducer(k, v)  - function to be applied to generator of values
     kvfunc         - function to extract key and value from input line
    """
    for line in lines:
        k, v = kvfunc(line)
        mapper(k, v)

        
def sreduce(reducer, lines, kvfunc=tab_separator):
    """Stream reducer: groups lines by key and applies
    reducer function to the whole list of values.
    
     lines          - generator of key-value lines
     reducer(k, vs) - function to be applied to generator of values
     kvfunc         - function to extract key and value from input line
    """
    data = (kvfunc(line) for line in lines)
    for key, group in it.groupby(data, key=op.itemgetter(0)):
        reducer(key, (v for k, v in group))
