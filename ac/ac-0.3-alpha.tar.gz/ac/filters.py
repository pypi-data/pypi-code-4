def remove_empty(entry):
    """
        Filters all empty strings and 'None' entries from a list
    """
    return len(entry) >=1 

def nonalpha_filter(element):
    """
        Removes non-alpha characters from a filtered string.
    """
    return element in string.ascii_letters

def alphaonly(string):
    """
        Given a string, filters out all non-alpha characters
    """
    string = list(string)
    string = filter(nonalpha_filter,string)
    string = "".join(string)
    return string
