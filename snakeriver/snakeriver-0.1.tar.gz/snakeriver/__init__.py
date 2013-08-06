
import itertools as it
        
def smap(lines, mapper, sep='\t'):
    """Stream map: applies mapper to each line in input stream
    reducer function to the whole list of values.
    
     lines          - generator of key-value lines
     reducer(k, v) - function to be applied to generator of values
     sep            - optional separator for keys and values in line
    """
    for k, v in lines:
        mapper(k, v)

        
def sreduce(lines, reducer, trans=lambda x: x, sep='\t'):
    """Stream reducer: groups lines by key and applies
    reducer function to the whole list of values.
    
     lines          - generator of key-value lines
     reducer(k, vs) - function to be applied to generator of values
     trans          - optional transformer function to be applied to each value
     sep            - optional sep for keys and values in line
    """
    data = (line.strip().split(delim) for line in lines)
    for key, group in it.groupby(data, key=op.itemgetter(0)):
        reducer(key, (trans(v) for k, v in group))
