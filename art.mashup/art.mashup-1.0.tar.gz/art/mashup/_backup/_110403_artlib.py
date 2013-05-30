# -*- coding: utf-8 -*-
"""Art utilities library
"""

#~ def uniEncode(data):
    #~ """uniencode data
    #~ """
    #~ encodings = ('ascii', 'cp1252', 'iso-8859-1', 'utf-8', 'euc-jp', 'sjis', 'utf-16-le', 'utf-16-be')
#~
    #~ for i in encodings:
	#~ try:
	    #~ return unicode(data, i)
	#~ except:
	    #~ pass
#~
    #~ return data


def reverseDict (dictionary):
    return dict([(val, key) for (key, val) in dictionary.items()])


def decodeHtmlSpecialChars(s):
    import re
    def decodeEntity(matchObj):
	entity = matchObj.group(3)
	if matchObj.group(1) == '#':
	    # decoding by number
            if matchObj.group(2) == 'x':
                # number is hex
                return unichr(int(entity, 16))
            else:
                # number is decimal
                return unichr(int(entity))
	else:
	    # decoding by name
	    import htmlentitydefs
            codePoint = htmlentitydefs.name2codepoint[entity]
            if codePoint:
		return unichr(codePoint)
            else:
		return matchObj.group()

    return re.sub(r'&(#?)(x?)(\w+);', decodeEntity, s)