
import string
import types

QUOTEMAPPING = {
    "'" : u"'",
    '"' : u'"',
    '\\' : u'\\',
    '/' : u'/',
    'b' : unichr(8),
    'f' : unichr(0xc),
    'n' : unichr(0xa),
    'r' : unichr(0xd),
    't' : unichr(9),
    }

INVQUOTEMAPPING = {}
for (k,v) in QUOTEMAPPING.items():
    INVQUOTEMAPPING[v] = k

def myunicode(x):
    if type(x) is types.UnicodeType:
        return x
    return unicode(str(x), "utf-8", "ignore")

def formatString(s, mapper=INVQUOTEMAPPING):
    if type(s) is not types.UnicodeType:
        s = unicode(s, 'utf-8', 'ignore')
    L = ['"']
    for c in s:
        mc = mapper.get(c)
        if mc is None:
            L.append(c)
        else:
            L.append(u"\\"+mc)
    L.append('"')
    return "".join(L)

def formatIfNotString(v):
    "only format if not a string"
    if type(v) in types.StringTypes:
        return v
    return format(v, readable=False)

def format(jsonCompatibleValue, readable=True):
    L = list(formatValue(jsonCompatibleValue, readable=readable))
    return "".join(L)

def formatValue(jsonCompatibleValue, readable=True, indent="",
                seqTypes=(types.ListType, types.TupleType)):
    "quick and dirty converter generator primarily for testing"
    # initial indent is handled by caller
    if readable:
        indent2 = "   "+indent
    else:
        indent2 = indent
    v = jsonCompatibleValue
    tv = type(v)
    if tv in types.StringTypes:
        yield formatString(v)
    elif v is True:
        yield "true"
    elif v is False:
        yield "false"
    elif v is None:
        yield "null"
    elif tv in seqTypes:
        if len(v)<1:
            if readable:
                yield "[ ]"
            else:
                yield "[]"
        else:
            yield "["
            inside = False
            for e in v:
                if inside:
                    yield ","
                if readable:
                    yield "\n"
                    yield indent
                for x in formatValue(e, readable, indent2):
                    yield x
                inside = True
            if readable:
                yield "\n"
                yield indent
            yield "]"
    elif tv is types.DictType:
        items = v.items()
        items.sort()
        if len(items)<1:
            if readable:
                yield "{ }"
            else:
                yield "{}"
        else:
            yield "{"
            inside = False
            for (k,kv) in items:
                if type(k) not in types.StringTypes:
                    raise ValueError, "cannot have non string as key in json dictionary "+repr(type(k))
                if inside:
                    yield ","
                if readable:
                    yield "\n"
                    yield indent
                yield formatString(k)
                if readable:
                    yield " : "
                else:
                    yield ":"
                for x in  formatValue(kv, readable, indent2):
                    yield x
                inside = True
            if readable:
                yield "\n"
                yield indent
            yield "}"
    elif tv is types.LongType:
        yield repr(v)[:-1] # trim off the "L"
    else:
        # cross you fingers for other types and use repr...
        yield repr(v) # should work for most numbers???

def stringAsJsonSequence(inString):
    """parse string as sequence of json objects separated by white space (for indexing notations x[1][2]["this"]...)"""
    if type(inString) not in types.StringTypes:
        raise ValueError, "cannot parse non-string as sequence "+repr(type(inString))
    lString = len(inString)
    result = []
    endIndex = 0
    while endIndex<lString:
        (test, value, endIndex) = parseValue(inString, endIndex)
        if test:
            result.append(value)
        else:
            raise ValueError, "json parse failed: "+repr(inString[:100])
    return result

def stringAsJson(inString):
    # if not a string, leave it alone
    if type(inString) not in types.StringTypes:
        return inString
    lString = len(inString)
    (test, value, endIndex) = parseValue(inString)
    if test:
        if endIndex!=lString:
            raise ValueError, "tail of string not consumed "+repr((endIndex, lString))
        return value
    # otherwise the parse failed
    c1 = inString[max(0, endIndex-20) : endIndex]
    c2 = inString[endIndex : endIndex+20]
    raise ValueError, "json parse failed "+repr((value, c1, c2))
    
def parseValue(inString, startIndex=0,
               skipTrailingWhiteSpace=True,
               stringOnly=False,
               WHITESPACE=string.whitespace,
               DIGITS=string.digits,
               #HEXDIGITS=string.hexdigits,
               QUOTEMAP=QUOTEMAPPING
               ):
    "return (True, parsedValue, endIndex) or (False, StringExplanation, FailureIndex)"
    # skip initial whitespace (probably should use a regex...)
    lenString = len(inString)
    if startIndex<0:
        raise ValueError, "cannot search string before index 0"
    if lenString<=startIndex:
        return (False, "bad start index", startIndex)
    thisChar = None
    thisIndex = None
    i = startIndex
    while thisIndex is None:
        try:
            thisChar = inString[i]
        except IndexError:
            return (False, "past end of string skipping initial whitespace", i)
        if not thisChar in WHITESPACE:
            # special case (javascript style comment) if "//" then skip to newline or eof
            if thisChar=="/" and inString[i:i+2]=="//":
                endOfComment = inString.find("\n", i)
                if endOfComment<i:
                    endOfComment = lenString-1
                i = endOfComment+1
            else:
                thisIndex = i
                break
        i += 1
    if thisIndex is None:
        assert startIndex>=lenString
        return (False, "searched for json value starting past string end", startIndex)
    if stringOnly and thisChar!='"':
        return (False, "didn't find initial double quote searching in string only mode", thisIndex)
    # parse an object based on dispatching first character
    valueSet = False
    valueFound = None
    # Json strings hacked to accept single quotes even though its not in the spec
    if thisChar=='"' or thisChar=="'":
        quoteMark = thisChar
        # find a string
        accumulator = []
        cursor = thisIndex+1
        thisChar = inString[cursor]
        while thisChar!=quoteMark:
            # find first quote and backslash past cursor
            qIndex = inString.find(quoteMark, cursor)
            bsIndex = inString.find('\\', cursor)
            if qIndex<0:
                return (False, "scanned in string past last possible close quote", cursor)
            if bsIndex>=0 and bsIndex<qIndex:
                # parse a prefix and a quoted value \r or \u010e etc
                if bsIndex>cursor:
                    prefix = inString[cursor:bsIndex]
                    accumulator.append(prefix)
                    cursor = bsIndex
                cursor += 1
                if cursor>=lenString:
                    return (False, "cannot interpret backslash at end of string", cursor)
                indicator = inString[cursor]
                mapped = QUOTEMAP.get(indicator)
                if mapped is not None:
                    # \b etcetera: add translation
                    accumulator.append(mapped)
                    cursor += 1
                elif indicator=='u':
                    # four digit hexidecimal unicode character
                    hexstart = cursor+1
                    hexend = hexstart+4
                    hexcode = inString[hexstart:hexend]
                    if len(hexcode)!=4:
                        return (False, "unicode hex code must have 4 digits", cursor)
                    try:
                        hexvalue = int(hexcode, 16)
                    except ValueError:
                        return (False, "bad hexidecimal digits", cursor)
                    try:
                        unicodeCharacter = unichr(hexvalue)
                    except ValueError:
                        return (False, "bad unicode ordinal", cursor)
                    accumulator.append(unicodeCharacter)
                    cursor = hexend
                else:
                    return (False, "unknown character encoding indicator", cursor)
            else:
                # extract string up to the quote
                remainder = inString[cursor:qIndex]
                accumulator.append(remainder)
                cursor = qIndex
            thisChar = inString[cursor]
        # advance past close quote
        thisIndex = cursor+1
        #pr "accumulator", accumulator
        accumulator = map(myunicode, accumulator)
        valueFound = u"".join(accumulator)
        valueSet = True
    elif thisChar=='{':
        # find an 'object'
        valueFound = {}
        valueSet = True
        cursor = thisIndex+1
        closeFound = False
        while not closeFound: # and cursor<lenString:
            for i in xrange(cursor, lenString+1):
                try:
                    thisChar = inString[i]
                except IndexError:
                    return (False, "past end of string searching for closing '}'", cursor)
                if not thisChar in WHITESPACE:
                    cursor = i
                    break
            if thisChar=='}' and not valueFound:
                # found end of empty object
                closeFound = True
                cursor += 1
            else:
                # find a key string
                test = parseValue(inString, cursor, stringOnly=True)
                (more, value, nextcursor) = test
                if more:
                    cursor = nextcursor
                    currentKey = value
                else:
                    return test # propagate the complaint
                # find a colon
                thisChar = inString[cursor]
                if thisChar==":":
                    cursor += 1
                else:
                    return (False, "after key string did not find colon ':'", cursor)
                # find a map value
                test = parseValue(inString, cursor)
                (more, value, nextcursor) = test
                if more:
                    cursor = nextcursor
                    currentValue = value
                    valueFound[currentKey] = currentValue
                else:
                    return test # propagate the complaint
                # find a comma or a close bracket
                if cursor>=lenString:
                    return (False, "end of string after key/value pair with no close bracket", cursor)
                thisChar = inString[cursor]
                if thisChar==",":
                    # loop again
                    cursor += 1
                elif thisChar=="}":
                    # end of object
                    cursor += 1
                    closeFound = True
                else:
                    return (False, "after key/value pair did not find comma or close bracket", cursor)
        thisIndex = cursor
    elif thisChar=='[':
        # find an array
        valueFound = []
        valueSet = True
        cursor = thisIndex+1
        closeFound = False
        while not closeFound:# and cursor<lenString:
            for i in xrange(cursor, lenString+1):
                try:
                    thisChar = inString[i]
                except IndexError:
                    return (False, "past end of string searching for closing ']'", cursor)
                if not thisChar in WHITESPACE:
                    cursor = i
                    break
            if thisChar==']' and not valueFound:
                # found end of empty array
                closeFound = True
                cursor += 1
            else:
                # bracket not found, or looping past a comma: must find a valid value
                test = parseValue(inString, cursor)
                (more, value, nextcursor) = test
                if more:
                    cursor = nextcursor
                    valueFound.append(value)
                else:
                    return test # propagate the complaint
                # cursor should be at "," to continue or "]" to stop
                if cursor>=lenString:
                    return (False, "past end of string looking for comma or close bracket in array", cursor)
                thisChar = inString[cursor]
                if thisChar=="]":
                    closeFound = True
                    cursor += 1
                elif thisChar==",":
                    cursor += 1 # skip the comma and loop
                else:
                    return (False, "after value expect comma or array close bracket", cursor)
        assert valueFound is not None
        # ???? convert to tuple for safety....
        valueFound = tuple(valueFound)
        thisIndex = cursor
    elif thisChar=='t':
        # find true
        endIndex = thisIndex+4
        if inString[thisIndex:endIndex]=='true':
            valueFound = True
            valueSet = True
            thisIndex = endIndex
        else:
            return (False, "only token that starts with 't' should be 'true'", thisIndex)
    elif thisChar=='f':
        # find false
        endIndex = thisIndex+5
        if inString[thisIndex:endIndex]=='false':
            valueFound = False
            valueSet = True
            thisIndex = endIndex
        else:
            return (False, "only token that starts with 'f' should be 'false'", thisIndex)
    elif thisChar=='n':
        # find null
        endIndex = thisIndex+4
        if inString[thisIndex:endIndex]=='null':
            valueFound = None
            valueSet = True
            thisIndex = endIndex
        else:
            return (False, "only token that starts with 'n' should be 'null'", thisIndex)
    else:
        # find a number (only remaining option)
        cursor = thisIndex
        isInteger = True
        # skip initial -, if present
        if thisChar=='-':
            cursor+=1
            if cursor>=lenString:
                return (False, "cannot parse single hyphen at end of string", cursor)
            thisChar = inString[cursor]
        # accept a single 0 or nonzero followed by digits
        if thisChar=='0':
            cursor+=1
            if cursor>=lenString:
                thisChar = None # zero at end of string
            else:
                thisChar = inString[cursor]
        elif thisChar and thisChar in DIGITS:
            # accept non-zero digit followed by optional digits
            nextChar = None
            for i in xrange(cursor+1, lenString):
                c = inString[i]
                if not c in DIGITS:
                    cursor = i
                    nextChar = c
                    break
            if nextChar is None:
                cursor = lenString # digits to the end
                thisChar = None
            else:
                thisChar = nextChar
        else:
            return (False, "expect digit or indicator for start of JSON object (\"{[-tfn)", cursor)
        # optionally accept a dot followed by digit sequence
        if thisChar==".":
            isInteger = False
            cursor += 1
            if cursor>=lenString:
                return (False, "end of string after dot parsing number", cursor)
            thisChar = inString[cursor]
            endOfDecimal = None
            for i in xrange(cursor, lenString):
                nextChar = inString[i]
                if not nextChar in DIGITS:
                    endOfDecimal = i
                    thisChar = nextChar
                    break
            if endOfDecimal is None:
                # digits to end
                thisChar = None
                cursor = lenString
            else:
                if endOfDecimal<=cursor:
                    return (False, "digit must follow dot in number", cursor)
                cursor = endOfDecimal
                if cursor<lenString:
                    thisChar = inString[cursor]
                else:
                    thisChar = None
        # optionally accept exponent
        if thisChar and thisChar in "eE":
            isInteger = False
            cursor+=1
            if cursor>=lenString:
                return (False, "exponent in number cannot end string at 'E'", cursor)
            # accept a single + or -
            thisChar = inString[cursor]
            if thisChar in "+-":
                cursor+=1
                if cursor>=lenString:
                    return (False, "exponent cannot end string at sign (+-)", cursor)
                thisChar = inString[cursor] # redundant?
            endOfExponent = None
            for i in xrange(cursor, lenString):
                nextChar = inString[i]
                if not nextChar in DIGITS:
                    endOfExponent = i
                    thisChar = nextChar
                    break
            if endOfExponent is None:
                # digits to end
                thisChar = None
                cursor = lenString
            else:
                if endOfExponent<=cursor:
                    return (False, "exponent must include a digit", cursor)
                cursor = endOfExponent
        # parse the value
        valueString = inString[thisIndex:cursor]
        thisIndex = cursor
        valueSet = True
        if isInteger:
            valueFound = int(valueString)
        else:
            valueFound = float(valueString)
    assert valueSet
    if skipTrailingWhiteSpace:
        thisChar = None
        skipIndex = None
        for i in xrange(thisIndex, lenString):
            thisChar = inString[i]
            if thisChar not in WHITESPACE:
                skipIndex = i
                break
        if skipIndex is not None:
            thisIndex = skipIndex
        else:
            thisIndex = lenString
    return(True, valueFound, thisIndex)

def tupleize(x):
    tx = type(x)
    if tx in (types.ListType,types.TupleType):
        Lx = [ tupleize(e) for e in x ]
        return tuple(Lx)
    if tx is types.DictType:
        D = {}
        for (k,v) in x.items():
            D[k] = tupleize(v)
        return D
    return x

def checkEqual(inString, startIndex, expectedValue, expectedLength=None):
    expectedValue = tupleize(expectedValue)
    if expectedLength:
        expectedEnd = startIndex+expectedLength
    (flag, value, endIndex) = parseValue(inString, startIndex)
    if not flag:
        raise ValueError, "parse failed "+value+" "+str(endIndex)
    if value!=expectedValue:
        raise ValueError, "got unexpected value "+repr((value,expectedValue, inString[startIndex:]))
    if expectedLength and expectedEnd!=endIndex:
        raise ValueError, "end doesn't match "+repr((expectedEnd, endIndex, inString[startIndex:expectedEnd], inString[startIndex:endIndex]))
    print "verbose: checkEqual", (inString, startIndex, expectedValue, expectedLength)

def checkFail(inString, startIndex=0):
    (flag, value, endIndex) = parseValue(inString, startIndex)
    if flag:
        raise ValueError, "bogus successful parse "+repr((inString, startIndex, flag, value, endIndex))
    print "verbose: checkFail", (inString, startIndex, value, endIndex)

def checkNumberNear(inString, startIndex, expectedValue, expectedLength, epsilon=1e-15):
    expectedEnd = startIndex+expectedLength
    (flag, value, endIndex) = parseValue(inString, startIndex)
    if not flag:
        raise ValueError, "parse failed "+value+" "+str(endIndex)
    if abs(value-expectedValue)>epsilon:
        raise ValueError, "got unexpected value "+repr((value,expectedValue, inString[startIndex:]))
    if expectedEnd!=endIndex:
        raise ValueError, "end doesn't match "+repr((expectedEnd, endIndex, inString[startIndex:expectedEnd], inString[startIndex:endIndex]))
    print "verbose: checkNumberNear", (inString, startIndex, expectedValue, expectedLength)

def checkRoundTrip(v):
    fmt = formatValue(v)
    fmtlist = list(fmt)
    fmtstr = "".join(fmtlist)
    print "verbose: check round trip"
    print "verbose: ", fmtstr
    checkEqual(fmtstr, 0, v, len(fmtstr))
    
def test0():
    checkRoundTrip(0)
    checkRoundTrip(0.1)
    checkRoundTrip(2)
    checkRoundTrip(True)
    checkRoundTrip(False)
    checkRoundTrip(None)
    checkRoundTrip([])
    checkRoundTrip([1, "this", None])
    checkRoundTrip({"a": ["this"]})
    checkRoundTrip({})
    checkRoundTrip("this")
    checkRoundTrip('"this"')
    checkEqual("0", 0, 0, 1)
    checkFail("",0)
    checkFail("    ", 0)
    checkFail("e10",0)
    checkFail("    -", 0)
    checkEqual("00", 0, 0, 1) # parse only first digit
    checkEqual("0123", 0, 0, 1) # parse only first digit
    checkEqual("10", 0, 10, 2) 
    checkEqual("10  ", 0, 10, 4) 
    checkEqual(" -10   ", 0, -10) 
    checkEqual("  10  ", 0, 10, 6) 
    checkEqual("10a", 0, 10, 2) # parse up to "a" 
    checkEqual("  10a", 0, 10, 4) 
    checkEqual("  10a", 3, 0, 1)
    checkFail("  10a", 4)
    checkFail("10.", 0)
    checkFail("10.a", 0)
    checkNumberNear("10.2", 0, 10.2, 4)
    checkNumberNear("10.2e-1", 0, 1.02, 7)
    checkNumberNear("10.2e+1", 0, 102, 7)
    checkNumberNear("10.2e1", 0, 102, 6)
    checkNumberNear("10.2e1abc", 0, 102, 6)
    checkFail("10.1e", 0)
    checkFail("10.1e-", 0)
    checkFail("10.1e-abc", 0)
    checkFail("nubber", 0)
    checkEqual("null", 0, None, 4)
    checkEqual("nulla", 0, None, 4)
    checkEqual("  nulla", 0, None, 6)
    checkEqual("  null a", 0, None, 7)
    checkEqual("VAnull a", 2, None, 5)
    checkEqual("true ", 0, True, 5)
    checkEqual(" false", 0, False, 6)
    checkEqual("[]", 0, [], 2)
    checkEqual(" [ ] ", 0, [], 5)
    checkEqual("[1]", 0, [1], 3)
    checkEqual("[2,1]", 0, [2,1], 5)
    checkEqual(" [ 2 , 1 ] ", 0, [2,1], 11)
    checkEqual(" [ 2 , [1,2] ] ", 0, [2,[1,2]])
    checkFail("[1 5]")
    checkFail("[3, 5a]")
    checkFail("[34, 5")
    checkEqual("{}", 0, {}, 2)
    checkEqual(" { } ", 0, {}, 5)
    checkFail("{ 1: 1 }")
    checkEqual(' "this" ', 0, u"this")
    checkEqual(" 'this' ", 0, u"this")
    checkEqual(" 'this\\'\\\"' ", 0, u"this'"+'"')
    checkEqual(' "this \\b \\f \\n \\r \\t "', 0, "this \b \f \n \r \t ")
    checkEqual(' "\\b\\f\\n\\r\\t"', 0, "\b\f\n\r\t")
    checkEqual(' " \\\\n " ', 0, " \\n ")
    checkEqual(' " \\\\n\\\\n " ', 0, " \\n\\n ")
    checkFail('"   \\')
    checkFail('"  ')
    checkFail('   ')
    checkEqual('  "\u0101"  ', 0, unichr(0x0101))
    checkFail('"\u010"')
    checkEqual('  "this\u0101that"  ', 0, "this"+unichr(0x0101)+"that")
    checkFail("abc")
    checkEqual('{"this":     1231}', 0, {"this":     1231})
    checkEqual('''
                  // ignore this comment
                  {"this":
                  // and this one
                  1231}
                  // and this one too
                  ''', 0, {"this":     1231})
    checkEqual('{"this":     [1231,6,"b"]}', 0, {"this":     [1231,6,"b"]})
    checkFail('{"this":     [1231,6,"b"]')
    checkEqual('{"a": 1, "B": 2}', 0, {"a": 1, "B": 2})
    checkFail('{"a": 1, "B"}')
    checkFail('{"a": 1, "B":}')
    checkFail('{"a": 1, "B":0')
    checkFail('{"a": 1, "B":0 "hi there!"')

if __name__=="__main__":
    test0()
