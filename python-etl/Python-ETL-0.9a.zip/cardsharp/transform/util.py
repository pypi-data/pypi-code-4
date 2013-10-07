
__all__ = ['key_as_str']

def key_as_str(value, inner_trim=True):
    """Produces a key value for looking up in a crosswalk.
    
    If value is None than returns an empty string.
    >>> v = None
    >>> key_as_str(v) + 'XXX'
    'XXX'
    
    If value is a basestring removes leading and trailing whitespace if inner_trim = True, 
    multiple line spaces made into one space, value is lowered: 
    >>> v = '  DS     sS    '
    >>> key_as_str(v)
    'ds ss'
    
    If inner_trime is false just strim leading and trailing and lower
    >>> v = '   DF     sdsD'
    >>> key_as_str(v, inner_trim=False)
    'df     sdsd'
    """
    
    if value is None:
        return ''
    else:
        if isinstance(value, basestring):
            if inner_trim:
                return ' '.join(value.split()).lower()
            else:
                return value.strip().lower()
        else:
            return str(value)