
def parseColumn(string):
    """ Parses a column definition
    """
    col = string.split(':')
    column = {'name': col[0].strip(),
              'title': col[1].strip(),
              'type': col[2].strip()}
    for flag in col[3:]:
        column[flag.strip()] = True
    return column
