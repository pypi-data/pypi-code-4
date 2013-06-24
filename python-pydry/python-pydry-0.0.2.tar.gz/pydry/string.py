import re

def str_single_space(string):
    """ Converts more than one consecutive spaces into a single space """

    txt = re.sub(" +", ' ', string)
    return txt

def str_single_line(string):
    """ Converts a content with multiple line into a single line content """

    txt = re.sub("\r\n|\n|\r|\t", ' ', string)
    return txt

def str_serialize_clean(string):
    """ Converts content into a single line with single spaces """

    txt = str_single_space(str_single_line(string))
    return txt

def str_find_between_regex(string, start='', end='',  lazy=True, options=re.DOTALL|re.MULTILINE, allmatch=False, case=True):
    """ Returns substring between two strings tags. all=(returns all matches), lazy=(return shortest match)"""

    if not case:
        options |= re.IGNORECASE

    pattern = '{0}{1}{2}'.format('(?<={0})'.format(re.escape(start)) if start else '^',
                                 '(.*?)' if lazy else '(.*)',
                                 '(?={0})'.format(re.escape(end)) if end else '$')
    match = re.findall(pattern, string, options)
    if match:
        if allmatch:
            return match
        else:
            return match[0]
    return ''

def str_find_between_tags(string, start='', end='', case=True):
    """ Returns a substring between two string tags """

    if not case:
        string_orig = string
        string = string.lower()
        start = start.lower()
        end = end.lower()

    if start:
        s = string.find(start)
    else:
        s = 0

    if end:
        e = string.find(end, s+len(start))
    else:
        e = len(string)

    if s < 0 or e < 0:
        return ''

    if not case:
        return string_orig[s+len(start):e]
    return string[s+len(start):e]

def str_find_all_between_tags(string, start='', end='', case=True):
    """ Returns all substrings between two string tags """

    if not case:
        string_orig = string
        string = string.lower()
        start = start.lower()
        end = end.lower()

    results = []
    while True:

        if start:
            s = string.find(start)
        else:
            s = 0

        if end:
            e = string.find(end, s+len(start))
        else:
            e = len(string)

        if s < 0 or e < 0:
            break

        if not case:
            match = string_orig[s+len(start):e]
            string_orig = string_orig[e+len(end):]
        else:
            match = string[s+len(start):e]
        results.append(match)
        string = string[e+len(end):]
    return results


def str_find_between_tags_r(string, start='', end='', case=True):
    """ Returns a substring between two string tags - Start from end of string """

    if not case:
        string_orig = string
        string = string.lower()
        start = start.lower()
        end = end.lower()

    if end:
        e = string.rfind(end)
    else:
        e = len(string)

    if start:
        if end:
            s = string.rfind(start, len(end))
        else:
            s = string.rfind(start)
    else:
        s = 0

    if s < 0 or e < 0:
        return ''

    if not case:
        return string_orig[s+len(start):e]
    return string[s+len(start):e]

def str_text_tokenizer(string):
    """ 
    Tokenize the input string and return two lists, exclude list is for words that
    start with a dash (ex: -word) and include list is for all other words
    """

    # Regex to split on double-quotes, single-quotes, and continuous non-whitespace characters.
    split_pattern = re.compile('("[^"]+"|\'[^\']+\'|\S+)')
    
    # Pattern to remove more than one inter white-spaces and more than one "-"
    space_cleanup_pattern = re.compile('[\s]{2,}')
    dash_cleanup_pattern = re.compile('^[-]{2,}')
    
    # Return the list of keywords.
    keywords = [dash_cleanup_pattern.sub('-', space_cleanup_pattern.sub(' ', t.strip(' "\''))) \
                    for t in split_pattern.findall(string) \
                        if len(t.strip(' "\'')) > 0]
    include = [ word for word in keywords if not word.startswith('-')]
    exclude = [ word.lstrip('-') for word in keywords if word.startswith('-')]
    return include, exclude







