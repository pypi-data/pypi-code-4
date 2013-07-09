
import sys
import string
import rdjson.jsonParse
import whiffenv

JSON_DESCRIPTOR_ERROR = ValueError

def quoteText(t):
    "quote text so that parsing will regenerate t"
    t = t.replace("$", "$$")
    t = t.replace("{{", "{${")
    t = t.replace("}}", "}$}")
    return t

def dropQuotes(name, quotes= "\"'"):
    if name and len(name)>1 and name[0] in quotes and name[-1]==name[0]:
        return name[1:-1]
    return name

def parse_json_descriptor(inString, cursor, forbiddenInName="}", tooLongName=256):
    "return (True, dict, endcursor) for success or (False, message, errorLocation) for failure"
    #p "parse_json_descriptor", (cursor, inString[cursor:cursor+20])
    # quick and dirty for now
    accumulator = {}
    done = False
    lenString = len(inString)
    while not done:
        # look for a name terminated by :
        colonLocation = inString.find(":", cursor)
        if colonLocation<0:
            if accumulator:
                return (False, "Looking for name: json-data -- possibly after comma expect to find name terminated by colon at", cursor)
            # otherwise return empty structure
            break
        nameContainer = inString[cursor:colonLocation]
        if forbiddenInName in nameContainer:
            if accumulator:
                return (False, "Looking for name: json-data possibly after ',' -- could not find name delimited by ':' before forbidden char "+repr(forbiddenInName), cursor)
            # otherwise return empty structure
            break
        sNameContainer = nameContainer.split()
        if len(sNameContainer)!=1:
            if accumulator:
                return (False, "Lookng for name: json-data possibly after comma -- expect to find name containing no white followed by colon", cursor)
            # otherwise return an empty structure
            break
        theName = sNameContainer[0]
        theName = dropQuotes(theName)
        if len(theName)>tooLongName:
            return (False, "looking for name: json-data -- name too long", cursor)
        # otherwise the name is okay
        cursor = colonLocation+1
        # look for a json object
        (flag, jsonResult, endLocation) = rdjson.jsonParse.parseValue(inString, cursor)
        if not flag:
            return (False, jsonResult, endLocation) # propagate json parse failure
        # otherwise store the parsed object with the name
        cursor = endLocation
        accumulator[theName] = jsonResult
        # look for a , and loop if present
        if cursor<lenString and inString[cursor]==",":
            cursor += 1
            # loop...
        else:
            # end loop
            done = True
    # skip trailing ws
    cursor = skipws(inString, cursor)
    return (True, accumulator, cursor)

def matchAtCursor(inString, matchString, cursor, skipwhite=False):
    #pr "matchAtCursor", repr(matchString), repr(inString[cursor:cursor+len(matchString)]), cursor
    if skipwhite:
        #pr "skipping white space"
        cursor = skipws(inString,cursor)
    lenMatchString = len(matchString)
    lenInString = len(inString)
    if not lenMatchString:
        raise ValueError, "cannot match empty string"
    endMatch = cursor + lenMatchString
    if endMatch>lenInString or cursor<0:
        #pr "bad boundaries (endMatch, lenInString, cursor)", (endMatch, lenInString, cursor)
        return False
    testString = inString[cursor:endMatch]
    if testString==matchString:
        #pr "match found!"
        return endMatch
    else:
        #pr "no match", repr((testString, matchString))
        return False

def nextMatchEnd(inString, matchString, cursor):
    nextLocation = inString.find(matchString, cursor)
    if nextLocation<cursor:
        return False
    return nextLocation+len(matchString)

def skiptows(inString, cursor, forbidden="", QUOTES="\"'", WHITESPACE=string.whitespace):
    # someday do this with a regex, maybe
    lenString = len(inString)
    while cursor<lenString:
        c = inString[cursor]
        # skip over matching quotes
        while c in QUOTES:
            nextcursor = cursor+1
            while nextcursor<lenString and inString[nextcursor]!=c:
                nextcursor+=1
            if nextcursor>=lenString:
                prefix = inString[:cursor]
                nlines = len(prefix.split("\n"))
                raise ValueError, "near line "+str(nlines)+" unclosed quotes "+repr(inString[cursor:cursor+50])
            cursor = nextcursor+1
            if cursor>=lenString:
                return lenString
            c = inString[cursor]
        if c in forbidden or c in WHITESPACE:
            return cursor
        cursor+=1
    return lenString

def skipws(inString, cursor, WHITESPACE=string.whitespace):
    # someday do this with a regex, maybe
    lenString = len(inString)
    if cursor>=lenString:
        return lenString
    scanning = True
    while scanning:
        if cursor>=lenString:
            cursor = lenString
            scanning = False
        elif inString[cursor] in WHITESPACE:
            # skip white character
            cursor+=1
        else:
            test = matchAtCursor(inString, "{{comment", cursor)
            if test:
                # look for end of comment
                test2 = nextMatchEnd(inString, "}}", cursor+1)
                if test2:
                    if inString[test2-3:test2-2]!="/":
                        chunk = inString[cursor:test2]
                        bad = inString[test2-3:test2-2]
                        raise ValueError, "{{comment must end in /}} (not }}) "+repr((bad, chunk))
                    cursor = test2
                else:
                    raise ValueError, "'{{comment' not closed by '/}}'"
            else:
                # not white and not comment: end of scan
                scanning = False
    return cursor

def parse_page(inString, cursor=0, endMarker=None, file_path=None, name="[top level]"):
    pname = name
    # XXXX SOMEDAY REFACTOR THIS AND CLEAN IT UP.
    #p "parse_page", (cursor, inString[cursor:cursor+20])
    page_start = cursor
    thePage = page.Page(file_path)
    lenString = len(inString)
    if cursor>lenString:
        raise ValueError, "when parsing page [%s] content at start: cursor beyond string end "%pname+repr((cursor, lenString))
    # skip whitespace
    cursor = skipws(inString, cursor)
    # look for {{env .. /}} environment modifier
    test = True
    while test:
        test = matchAtCursor(inString, "{{env", cursor)
        if test and inString[test]=="-":
            test = False # may match get-env
        if test:
            cursor = test
            (success, result, nextcursor) = parse_json_descriptor(inString, cursor)
            if success:
                (test, message) = whiffenv.check_environment_message(result)
                if not test:
                    return (False, message, cursor)
                thePage.add_environment_dict(result)
                cursor = nextcursor
            else:
                return (False, result, nextcursor)
            test = matchAtCursor(inString, "/}}", cursor)
            if test:
                cursor = test
            else:
                #pr "json parse got", result
                return (False, "Parsing environment at page [%s] begin -- could not parse to end of '{{env' json specification: expect /}} or comma found:"%pname+repr(inString[cursor:cursor+4]), cursor)
    # look for {{require page formal parameters
    # OR cgi-default specifications 
    test = True    
    while test:
        scursor = skipws(inString, cursor)
        #p "looking for require at", repr(inString[scursor:scursor+20])
        test = matchAtCursor(inString, "{{require", scursor)
        if test:
            cursor = test
            test = nextMatchEnd(inString, "}}", cursor+1)
            has_default_value = False
            if not test:
                return (False, "'Parsing page [%s] formal parameters -- {{require' not terminated by '}}'"%pname, cursor)
            elif inString[test-3:test]!="/}}":
                # form is {{require name}} page {{/require}}
                has_default_value = True
                #test = nextMatchEnd(inString, "}}", cursor+1)
                nameEnd = test-2
            else:
                # form is {{require name/}}
                nameEnd = test-3
            namechunk = inString[cursor:nameEnd]
            #p "namechunk", namechunk
            sname = namechunk.split()
            if len(sname)!=1:
                return (False, "parsing page [%s] formal argument {{require -- expect argument name containing no whitespace"%pname+repr(sname), cursor)
            name = sname[0]
            name = dropQuotes(name)
            default_value = None
            cursor = test
            if has_default_value:
                # parse a page terminated by {{/require}}
                (test, result, endLocation) = parse_page(inString, cursor, "{{/require}}", file_path=file_path, name=name)
                if test:
                    default_value = page.DeferPageBindings(result)
                    cursor = endLocation
                    # Eat the end {{/require}}
                    test = matchAtCursor(inString, "{{/require}}", cursor, True)
                    if test:
                        cursor = test
                    else:
                        return (False, 'parsing page [%s] formal argument [%s] -- after default page did not find "{{/require}}"'%(pname, name), cursor)
                else:
                    return (test, 'parsing page [%s] formal argument %s -- '%(pname,name)+result, endLocation) # pass on the complaint from page_parse
            #pr "add page require default", default_value
            thePage.add_require(name, default_value)
        else:
            test = matchAtCursor(inString, "{{cgi-default", scursor)
            if test:
                cursor = test
                # parse format {{cgi-default NAME}}VALUE{{/cgi-default}}
                test = nextMatchEnd(inString, "}}", cursor+1)
                if not test:
                    return (False, "parsing page [%s] formal parameters -- '{{cgi-default' not terminated by '}}'"%pname, cursor)
                nameEnd = test-2
                namechunk = inString[cursor:nameEnd]
                if not namechunk:
                    return (False, "parsing page [%s] formal parameters -- '{{cgi-default' has no name field"%pname, cursor)
                if namechunk[-1]=="/":
                    return (False, "parsing page [%s] formal parameters -- '{{cgi-default...}}' must be terminated with {{/cgi-default}} not /}}"%pname, cursor)
                sname = namechunk.split()
                if len(sname)!=1:
                    return (False, "parsing page [%s] formal parameters -- cgi-default name must contain no whitespace"%pname, cursor)
                name = sname[0]
                name = dropQuotes(name)
                cursor = test
                (test, result, endLocation) = parse_page(inString, cursor, "{{/cgi-default}}", file_path=file_path, name=name)
                if test:
                    # eat the end marker
                    cursor = endLocation
                    test = matchAtCursor(inString, "{{/cgi-default}}", cursor, True)
                    if not test:
                        #pr (cursor, inString[:cursor], inString[cursor:])
                        return (False, "parsing page [%s] formal parameters -- after '{{cgi-default' %s did not find {{/cgi-default}}"%(pname,name), cursor)
                    cursor = test
                    #pr "add cgi-default page", result
                    thePage.add_cgi_default(name, result)
                else:
                    # pass on page parsing complaint
                    return (False, 'parsing page [%s] formal parameters cgi-default %s -- '%(pname, name)+result, endLocation)
        # return to top of require search loop
    # parse remainder as stream components
    while cursor<lenString and not (endMarker and matchAtCursor(inString, endMarker, cursor, skipwhite=True)):
        #pr ; #pr "chunk", repr(inString[cursor:cursor+20])
        #pr "cursor, len", cursor, lenString
        #pr "endMarker", repr(endMarker)
        #if endMarker: #pr "matchAtCursor", matchAtCursor(inString, endMarker, cursor, skipwhite=True)
        (success, result, nextcursor) = parse_component(inString, cursor, file_path=file_path, name=pname)
        if success:
            thePage.add_component(result)
            cursor = nextcursor
        else:
            return (False, 'parsing page [%s] stream components -- '%pname+result, cursor) # pass on complaint
    page_end = cursor
    page_text = inString[page_start:page_end]
    thePage.text = page_text
    thePage.sanity_check()
    return (True, thePage, cursor)

def parse_argument_parameters(inString, cursor, endTag, nullpageOk=False, file_path=None):
    """
    if at 'name/}} then return (True, 'name', None, end_of_match)
    if at 'name}}pagetext then return (True, 'name', page, end_of_match)
    otherwise return a parse error (False, error_message, None, location_of_error)
    """
    nameEnd = inString.find('}}', cursor)
    endmark = '}}'
    if nullpageOk and nameEnd>cursor and inString[nameEnd-1]=='/':
        nameEnd -= 1
        endmark = '/}}'
    if nameEnd<=cursor:
        return (False, "argument ending '}}' not found", None, cursor)
    nameChunk = inString[cursor:nameEnd]
    sname = nameChunk.split()
    if len(sname)!=1:
        return (False, "argument requires name containing no whitespace: %s "%sname+repr(nameChunk), None, cursor)
    cursor = nameEnd + len(endmark)
    name = sname[0]
    name = dropQuotes(name)
    if '{' in name or '}' in name:
        return (False, "argument name cannot contain curly brackets: %s"%sname, None, nameEnd)
    if '/' in name:
        return (False, "argument name cannot end with or contain slash: %s"%sname, None, nameEnd)
    # don't parse the page if the tag was closed
    if endmark=="/}}":
        return (True, name, None, cursor)
    # otherwise parse page looking for endTag
    (test, result, endlocation) = parse_page(inString, cursor, endMarker=endTag, file_path=file_path, name=name)
    if test:
        cursor = endlocation
        thePage = result
    else:
        return (False, "parsing argument page %s -- "%sname+result, None, endlocation)
    test = matchAtCursor(inString, endTag, cursor, True)
    if test>cursor:
        return (True, name, thePage, test)
    else:
        return (False, "parsing argument page %s -- end marker not found "%sname+repr(endTag), None, cursor)

argument_kinds = "{{using {{data {{text {{set-cgi {{set-id {{use-include {{reuse"

def get_component_specs(inString, cursor, endMarker, file_path):
    #p "get_component_specs", (cursor, inString[cursor:cursor+20])
    error_prologue = "before "+repr(endMarker)+" -- "
    cursor = skipws(inString, cursor)
    tokenEnd = skiptows(inString, cursor, "/{}:")
    token = inString[cursor:tokenEnd]
    if not token:
        return (False, "no identifier found in specification", cursor)
    cursor = tokenEnd
    cursor = skipws(inString, cursor)
    (success, result, cursor) = parse_json_descriptor(inString, cursor)
    error_prologue = "parsing after identifier "+repr(token.strip())+" --  "+error_prologue
    if success:
        (test, message) = whiffenv.check_environment_message(result)
        if not test:
            return (False, error_prologue+" parsing json environment spec to '/}}' "+message, cursor)
        jsonDict = result
    else:
        return (False, error_prologue+" parsing json environment spec to '/}}' -- "+result, cursor) # pass on the complaint
    test = matchAtCursor(inString, "/}}", cursor, True)
    arguments = {}
    cgi_sets = {}
    id_sets = {}
    if test:
        # no arguments, cgi_sets
        cursor = test
    else:
        # look for set-cgi specifications
        # look for arguments
        test = matchAtCursor(inString, "}}", cursor, True)
        if not test:
            #raise ValueError, repr( (inString[:cursor], inString[cursor:]) )
            return (False, error_prologue+"expect close of tag after identifier and json environment spec", cursor)
        # look for {{using NAME}} PAGE {{/using}} or {{data or {{text or {{set-cgi until endMarker (or default page special case after the while loop)
        cursor = test
        parsingArgs = True
        pp = error_prologue+" -- looking for %s -- "%argument_kinds
        while parsingArgs:
            #pr "parsing args", (cursor, inString[cursor:cursor+20])
            cursor = skipws(inString, cursor)
            #pr "skipped to", (cursor, inString[cursor:cursor+20])
            testArg = matchAtCursor(inString, '{{using', cursor, True)
            testId = matchAtCursor(inString, '{{set-id', cursor, True)
            testData = matchAtCursor(inString, '{{data', cursor, True)
            testText = matchAtCursor(inString, '{{text', cursor, True)
            testCgiSet = matchAtCursor(inString, '{{set-cgi', cursor, True)
            testBindSection= matchAtCursor(inString, '{{reuse', cursor, True)
            testBindUrl = matchAtCursor(inString, '{{use-include', cursor, True)
            #test = testArg or testData or testText or testCgiSet or testId
            theArgument = None
            theCgi = None
            if testBindUrl or testBindSection:
                #pr "parsing bind"
                cursor = testBindUrl or testBindSection
                nameEnd = inString.find('/}}', cursor)
                if nameEnd<cursor:
                    return (False, pp+"argument ending '}}' not found", cursor)
                nameChunk = inString[cursor:nameEnd]
                sname = nameChunk.split()
                if len(sname)!=2:
                    return (False, pp+"bind arguments requires 2 names containing no whitespace", cursor)
                cursor = nameEnd+len('/}}')
                name = sname[0]
                name = dropQuotes(name)
                target = sname[1]
                target = dropQuotes(target)
                if testBindUrl:
                    #pr "binding url", (name, target)
                    theArgument = urlcomponent.UrlBinding(target)
                elif testBindSection:
                    #pr "binding using", (name, target)
                    theArgument = argcomponent.SectionBinding(target, file_path)
                else:
                    raise ValueError, "unreachable code"
                arguments[name] = theArgument
            elif testArg or testCgiSet or testId:
                #cursor = test
                if testArg:
                    endTag = "{{/using}}"
                    cursor = testArg
                elif testCgiSet:
                    endTag = "{{/set-cgi}}"
                    cursor = testCgiSet
                elif testId:
                    endTag = "{{/set-id}}"
                    cursor = testId
                else:
                    raise ValueError, "unreachable code"
                (test, name_or_error, page, end_of_match) = parse_argument_parameters(
                    inString, cursor, endTag, file_path=file_path)
                #pr "PARSE_ARG_PARAMS GIVES", (test, name_or_error, page, end_of_match)
                if not test:
                    return (False, pp+" -- looking for "+endTag+" -- "+name_or_error, end_of_match)
                name = name_or_error
                if testArg:
                    theArgument = page
                    #pr "ASSIGNING ARGUMENT", (name, theArgument)
                    arguments[name] = theArgument
                elif testCgiSet:
                    theCgi = page
                    cgi_sets[name] = theCgi
                elif testId:
                    id_sets[name] = page
                else:
                    raise ValueError, "unreachable code"
                cursor = end_of_match
                #pr "FOUND", (theArgument, theCgi)
                #pr "END AT", (inString[:cursor], inString[cursor:])
            elif testData or testText:
                #cursor = test
                cursor = testData or testText
                nameEnd = inString.find('}}', cursor)
                if nameEnd<cursor:
                    return (False, pp+"argument ending '}}' not found", cursor)
                nameChunk = inString[cursor:nameEnd]
                sname = nameChunk.split()
                if len(sname)!=1:
                    return (False, pp+"argument requires name containing no whitespace", cursor)
                cursor = nameEnd+len('}}')
                name = sname[0]
                name = dropQuotes(name)
                if "{" in name or "}" in name:
                    return (False, pp+"argument name apparently includes invalid delimiters { or }", cursor)
                if "/" in name:
                    return (False, pp+"argument name cannot contain or end with slash '/'", cursor)
                # now parse a page with end marker {{/using}}
                #if testArg:
                #    (test, result, endlocation) = parse_page(inString, cursor, endMarker='{{/using}}')
                #    if test:
                #        theArgument = result
                #        cursor = endlocation
                #    else:
                #        #pr "returning using page", result
                #        return (False, pp+result, endlocation) # pass on complaint
                #    test = matchAtCursor(inString, '{{/using}}', cursor, True)
                #if testCgiSet:
                #    # parse page ending {{/set-cgi}}
                #    (test, result, endlocation) = parse_page(inString, cursor, endMarker='{{/set-cgi}}')
                #    if test:
                #        theCgi = result
                #        cursor = endlocation
                #    else:
                #        #pr "returning set-cgi page", result
                #        return (False, error_prologue+"parsing {{set-cgi page argument -- "+result, endlocation) # pass on complaint
                #    test = matchAtCursor(inString, '{{/set-cgi}}', cursor, True) 
                if testData:
                    # parse a json object
                    (flag, jsonResult, endLocation) = rdjson.jsonParse.parseValue(inString, cursor)
                    if not flag:
                        return (False, error_prologue+"parsing {{data json argument -- "+repr(jsonResult), endLocation) # pass on the complaint
                    cursor = endLocation
                    theArgument = jsonResult
                    arguments[name] = theArgument
                    test = matchAtCursor(inString, '{{/data}}', cursor, True)
                elif testText:
                    # parse text
                    test = inString.find("{{/text}}", cursor)
                    if test>=cursor:
                        theArgument = inString[cursor:test]
                        arguments[name] = theArgument
                        cursor = test
                    else:
                        return (False, error_prologue+"parsing {{text argument -- cannot find closing '{{' after text", cursor)
                    test = matchAtCursor(inString, '{{/text}}', cursor, True)
                else:
                    raise ValueError, "unreachable code"
                if test>cursor:
                    #pr "advancing", (cursor, inString[cursor:test], test)
                    cursor = test
                else:
                    return (False, pp+"for argument did not find close tag", cursor)
                #if theArgument is not None:
                #    arguments[name] = theArgument
                #elif theCgi is not None:
                #    cgi_sets[name] = theCgi
                #else:
                #    raise ValueError, "unreachable code"
            else:
                # didn't find an argument -- continue with other elements
                #pr "done parsing arguments at", cursor
                parsingArgs = False
        # now eat the endmarker
        test = matchAtCursor(inString, endMarker, cursor, True)
        if test:
            #pr "FOUND ENDMARKER AT CURSOR"
            cursor = test
        else:
            #pr "DID NOT FIND END MARKER AT CURSOR", (endMarker, inString[:cursor], inString[cursor:])
            # SPECIAL CASE: if there are no arguments or set-cgi's try to parse a page as a single argument! and call it "page"
            #p "trying to parse default page", (inString[:cursor], inString[cursor:])
            if len(arguments)==0 and len(cgi_sets)==0 and len(id_sets)==0:
                (test, result, endlocation) = parse_page(inString, cursor, endMarker=endMarker, file_path=file_path, name=token)
                if test:
                    #p "parsed page", (cursor, test, inString[cursor:endlocation])
                    cursor = endlocation
                    #pr "assigning default page argument", result
                    arguments["page"] = result
                    # eat the end marker
                    test = matchAtCursor(inString, endMarker, cursor, True)
                    if test:
                        cursor = test
                    else:
                        return (test, error_prologue+"could not find "+repr(endMarker)+" after page end for single page argument", cursor)
                else:
                    return (test, error_prologue+result, endlocation) # pass on complaint
            else:
                #pr (endMarker, cursor, inString[:cursor], inString[cursor:])
                return (False, error_prologue+"did not find end marker "+repr(endMarker)+" after arguments", cursor)
    specs = (token, jsonDict, arguments, cgi_sets, id_sets)
    return (True, specs, cursor)

def get_simple_name(inString, cursor, tagname, default_value=False, terminator="/}}"):
    #pr "LOOKING FOR SIMPLE NAME"
    #pr "BEFORE", repr(inString[max(0, cursor-80):])
    #pr "AFTER", repr(inString[cursor: cursor+80])
    endMarkLocation = inString.find(terminator, cursor)
    if endMarkLocation<cursor:
        return (False, "parsing name -- '{{%s' not terminated by '%s'"%(tagname,terminator), cursor)
    nameChunk = inString[cursor:endMarkLocation]
    sname = nameChunk.split()
    if default_value is not False and len(sname)==0:
        name = default_value
    elif len(sname)!=1:
        if terminator=="/}}" and inString.find("}}", cursor)<endMarkLocation:
            return (False, "parsing name -- expect '{{%s' to terminate with '/}}', not '}}'"%(tagname,), cursor)
        return (False, "parsing name -- '{{%s' expects a single name with no white space"%(tagname,), cursor)
    else:
        name = sname[0]
    parse_end = endMarkLocation + len(terminator)
    name = dropQuotes(name)
    return (True, name, parse_end)

stream_components = "{{get-cgi, {{id, {{get-env, {{use, {{include, {{get-id"

def parse_component(inString, cursor, file_path, name=None):
    #pr "parse_component", (cursor, inString[max(0,cursor-20):cursor], inString[cursor:cursor+20])
    lenString = len(inString)
    startcursor = cursor
    # skip any comment and any whitespace following the comment
    if inString[cursor:cursor+2]=="{{":
        # might be at a comment, if so skip it
        #pr "trying to skip comments"
        cursor = skipws(inString, cursor)
    test = matchAtCursor(inString, "{{get-cgi", cursor, False)
    if test:
        (flag, info, index) = get_simple_name(inString, test, "get-cgi")
        if flag:
            name = info
            cursor = index
            theCgiComponent = cgicomponent.CgiComponent(name)
            return (True, theCgiComponent, cursor)
        else:
            return (flag, "parsing get-cgi components "+info, index) # propagate failure
    test = matchAtCursor(inString, "{{id", cursor, False)
    if test:
        (flag, info, index) = get_simple_name(inString, test, "id", default_value=None)
        if flag:
            name = info
            cursor = index
            theIdComponent = idcomponent.IdComponent(name)
            return (True, theIdComponent, cursor)
        else:
            return (flag, "parsing {{id --"+ info, index) # propagate failure
    test = matchAtCursor(inString, "{{get-env", cursor, False)
    if test:
        #p "attempting parse of get-env", (cursor, inString[cursor:cursor+20])
        #(flag, info, index) = get_simple_name(inString, test, "get-env")
        (flag, name_or_error, page, index) = parse_argument_parameters(
            inString, test, "{{/get-env}}", True, file_path=file_path)
        if flag:
            #name = info
            name = name_or_error
            cursor = index
            theNameComponent = namecomponent.NameComponent(name, page)
            #pr "successful parse of get-env", theNameComponent, cursor
            return (True, theNameComponent, cursor)
        else:
            return (False, "parsing {{get-env --"+name_or_error, index)
    test = matchAtCursor(inString, "{{get-id", cursor, False)
    if test:
        #p "attempting parse of get-id", (cursor, inString[cursor:cursor+20])
        #(flag, info, index) = get_simple_name(inString, test, "get-id")
        (flag, name_or_error, page, index) = parse_argument_parameters(
            inString, test, "{{/get-id}}", True, file_path=file_path)
        if flag:
            #name = info
            name = name_or_error
            cursor = index
            theNameComponent = namecomponent.NameComponent(name, page, use_prefix=True)
            #pr "successful parse of get-id", theNameComponent, cursor
            return (True, theNameComponent, cursor)
        else:
            return (False, "parsing {{get-id --"+name_or_error, index)
    test = matchAtCursor(inString, "{{use", cursor, False)
    if test:
        #p "attempting parse of use", (cursor, inString[cursor:cursor+20])
        cursor = test
        (success, specs, cursor) = get_component_specs(inString, cursor, "{{/use}}", file_path=file_path)
        if success:
            (argName, jsonDict, arguments, cgi_sets, id_sets) = specs
            #p "successful parse of use", (cursor, inString[cursor:cursor+20])
            theArgComponent = argcomponent.ArgComponent(argName, jsonDict, arguments, cgi_sets, id_sets)
            return (True, theArgComponent, cursor)
        else:
            return (False, "parsing {{use components -- "+specs, cursor) # pass on complaint
    test = matchAtCursor(inString, "{{include", cursor, False)
    if test:
        #p "attempting parse of include", (cursor, inString[cursor:cursor+20])
        cursor = test
        (success, specs, cursor) = get_component_specs(inString, cursor, "{{/include}}", file_path=file_path)
        if success:
            (theUrl, jsonDict, arguments, cgi_sets, id_sets) = specs
            if len(theUrl)<3 or not theUrl[0] in "\"'":
                #pr "inString"
                #pr repr(inString)
                #pr "text"
                #pr inString
                #pr "end"
                return (False, "'{{include' Url parameter must be non-empty and quoted", test)
            if theUrl[0]!=theUrl[-1]:
                return (False, "'{{include' Url parameter must be surrounded by matching quotes", test)
            theUrl = theUrl[1:-1]
            #p "successful parse of include", (cursor, inString[cursor:cursor+20])
            theUrlComponent = urlcomponent.UrlComponent(theUrl, jsonDict, arguments, cgi_sets, id_sets)
            return (True, theUrlComponent, cursor)
        else:
            return (False, "parsing include components --"+specs, cursor) # pass on the complaint
    # otherwise extract a text component
    #cursor += 1 # text must contain at least one character
    #pr "attempting parse of plain text", (cursor, inString[cursor:cursor+20])
    textEnd = inString.find("{{", cursor)
    if textEnd==cursor:
        #p inString[:cursor]
        #p "***", cursor, textEnd
        #p inString[cursor:]
        return (False, "{{ in using body must precede a recognized stream component ("+stream_components+"): use {${ to 'quote' {{ "+repr((cursor, inString[cursor:cursor+30])), cursor)
    if textEnd<cursor:
        textEnd = lenString # no following construct
    theText = inString[startcursor:textEnd]
    cursor = textEnd
    #pr "text with comments", repr(theText)
    cleanText = remove_comments(theText)
    #pr "text without comments", repr(cleanText)
    cleanText = cleanText.replace('{${', '{{')
    cleanText = cleanText.replace('}$}', '}}')
    cleanText = cleanText.replace("$$", "$")
    #pr "successful parse of plain text", (cursor, cleanText, inString[startcursor:cursor+20])
    theTextComponent = textcomponent.TextComponent(cleanText)
    return (True, theTextComponent, cursor)

def remove_comments(text):
    #p"cleaning", repr(text)
    accumulator = []
    cursor = 0
    commentStart = text.find("{{comment", cursor)
    while commentStart>=cursor:
        #p"removing comment at", commentStart
        keep = text[cursor:commentStart]
        #p"keeping", repr(keep)
        accumulator.append(keep)
        commentEnd = nextMatchEnd(text, '/}}', commentStart)
        if commentEnd<commentStart:
            raise ValueError, "unterminated comment at "+repr(cursor)
        #p"skipping", repr(text[commentStart:commentEnd])
        cursor = commentEnd
        commentStart = text.find("{{comment", cursor)
    accumulator.append(text[cursor:])
    #p"cleaned text", accumulator
    return "".join(accumulator)

# imports at bottom to avoid circularity problems
import textcomponent
import namecomponent
import urlcomponent
import argcomponent
import cgicomponent
import idcomponent
import page

# ==== testing stuff

def json_test():
    json_compare("", {})
    print "TESTING pass 1"
    json_compare(' a:"a" ', {"a":"a"})
    print "pass 2"
    json_compare(' a:"a", b:1 ', {"a":"a", "b":1})
    print "pass 3"
    json_compare(' a:"a", b:1 }} d:4', {"a":"a", "b":1})
    print "pass 4"
    print json_fail(' a:')
    print json_fail(' a:1,')
    print json_fail(' a:1, b')
    print json_fail(' a:1, b:')
    print json_fail(' a:[ }}')
    print json_fail(' a:1, b c:2')

def json_fail(inString):
    (flag, result, outCursor) = parse_json_descriptor(inString, 0)
    if flag:
        print "on failure test got success"
        print "string", repr(inString)
        print "result", repr(result)
    else:
        return "expected failure: "+repr( (inString, result) ) # a-ok

def json_compare(inString, testDict):
    (flag, outDict, outCursor) = parse_json_descriptor(inString, 0)
    if outDict!=testDict:
        print "json results don't match expected results"
        print "string", repr(string)
        print "expected", repr(testDict)
        print "got", repr(outDict)
        print "cursor", outCursor
        raise ValueError, "unexpected json result"
    else:
        return True # a-ok

def page_fail_check(inString):
    result = "exception"
    cursor = 0
    try:
        (success, result, cursor) = parse_page(inString, file_path="(test)")
    except:
        #print "expected failure by exception", repr(inString)
        result = repr(sys.exc_info()[1])
    else:
        if success:
            print "SUCCESS ON EXPECTED FAILURE"
            print "string", repr(inString)
            print "result dump", repr(result.dump())
            raise ValueError, "unexpected successful parse"
    print "page_fail_check", (inString,), "#", cursor, result

def page_fail_test():
    page_fail_check(' prefix {{include "../relative_url/}} body text')
    page_fail_check(' prefix {{include "../relative_url" a: [1,3/}} body text')
    page_fail_check(' {{comment }} ')
    page_fail_check(' {{env a:[1,3]/}} {{require boogie}} more stuff')
    page_fail_check(' {{env a:[1,3]/}} {{require bo ogie/}} more stuff')
    page_fail_check(' {{use a:1/}} ')
    page_fail_check(' {{use argggh a:[1/}} ')
    page_fail_check(' {{use argggh a:[1]}} {{using  {{/using}}{{/use}}{{/using}} {{/use}} ')
    page_fail_check(' {{use a}} {{using b}} {{/using}} {{comment invalid page}} {{/use}} ')
    page_fail_check(' {{use a}} {{using b}} {{/using}} {{require bo ogie/}} more stuff {{/use}} ')
    page_fail_check(' {{use a}} {{using b}} {{/aarg}} valid page {{/use}} ')
    page_fail_check(' {{whatever ')

def page_check(inString, expectedDump=None):
    #print "parsing page", repr(inString)
    (success, result, cursor) = parse_page(inString, file_path="(test)")
    if success:
        #print "parse succeeded"
        rdump = result.dump()
        #print "dump:", repr(rdump)
        if expectedDump is not None:
            if expectedDump==rdump:
                #print "dump matches expected dump"
                pass
            else:
                print "DUMP MATCH FAILS"
                print "expected", repr(expectedDump)
                print "derived", repr(rdump)
                raise ValueError, "parse produced bad dump"
        else:
            #print "no expected dump provided"
            pass
    else:
        print "PARSE FAILED"
        print (result, cursor)
        print (inString[:cursor], inString[cursor:])
        raise ValueError, "page parse failed"
    if cursor<len(inString):
        print "SUCCESSFUL PARSE DID NOT CONSUME ALL OF INPUT"
        print (inString[:cursor], inString[cursor:])
        raise ValueError, "parse leaves unparsed tail"
    if cursor>len(inString):
        print "SUCCESSFUL PARSE RETURNS TOO LARGE CURSOR"
        print (inString, len(inString), cursor)
    print "page_check", (inString, rdump)

def page_test():
    print "running page tests"
    page_check ('', '[]')
    page_check (' bare string ', '[]bare string ')
    page_check ('bare {{comment this is a comment/}} string.', '[]bare  string.')
    page_check (' {{comment env example/}} {{env a:"this"/}} body text', "[('a', u'this')] body text")
    page_check (' {{comment env example2/}} {{env a:"this", another:1/}} body text', "[('a', u'this'), ('another', 1)] body text")
    page_check (' {{require para/}} body text',
                "[]{{require 'para'/}} body text")
    page_check (' {{get-env name/}} body text', "[]{{get-env 'name'/}} body text")
    page_check (' prefix {{get-env name/}} body text', "[]prefix {{get-env 'name'/}} body text")
    page_check (' prefix {{use name/}} body text', "[]prefix {{use name []}}{{/use}} body text")
    page_check (' prefix {{include "../relative_url"/}} body text',
                "[]prefix {{include '../relative_url' []}}{{/include}} body text")
    page_check(' prefix {{include "../relative_url"/}} body text')
    page_check ('prefix {{include "../relative_url" envvar:46/}} body text',
                "[]prefix {{include '../relative_url' [('envvar', 46)]}}{{/include}} body text")
    page_check (' {{use argname}} {{/use}} body text',
                "[]{{use argname []}}{{/use}} body text")
    page_check (' {{use argname}} {{using name}} page argument {{/using}} {{/use}} body text',
                "[]{{use argname []}} {{using name}}[]page argument {{/using}} {{/use}} body text")
    page_check (' {{use argname}} {{using n1}} p1 {{/using}}{{using n2}} p2 {{/using}}  {{/use}} body text',
                "[]{{use argname []}} {{using n1}}[]p1 {{/using}}  {{using n2}}[]p2 {{/using}} {{/use}} body text")
    page_check (' {${whatever ', '[]{{whatever ')    
    page_check(' {{use argname}} {{using n1}} p1 {{/using}}{{using n2}} p2 {{/using}}  {{/use}} body text')
    page_check (' {{include "http://www.example.com/whatever"/}} ', "[]{{include 'http://www.example.com/whatever' []}}{{/include}} ")
    page_check (' {{include "abc"}}{{using p}}a page{{/using}}{{/include}}',
            u"[]{{include 'abc' []}} {{using p}}[]a page{{/using}} {{/include}}")
    page_check (' {{include "abc"}}{{text t}}{{/text}}{{using p}}a page{{/using}}{{/include}}',
            u"[]{{include 'abc' []}} {{using p}}[]a page{{/using}}  {{using t}}{{/using}} {{/include}}")
    page_check (' {{include "abc"}}{{data d}}{"this": ["that", "the-other"]}{{/data}}{{/include}}',
            u"[]{{include 'abc' []}} {{using d}}{u'this': [u'that', u'the-other']}{{/using}} {{/include}}")
    page_check (' {{include "abc"}}{{text t}}some text{{/text}}{{using p}}a page{{/using}}{{data d}}{"this": ["that", "the-other"]}{{/data}}{{/include}}',
            u"[]{{include 'abc' []}} {{using d}}{u'this': [u'that', u'the-other']}{{/using}}  {{using p}}[]a page{{/using}}  {{using t}}some text{{/using}} {{/include}}")
    page_check (' {{include "abc"}} default page argument {{/include}} ', u"[]{{include 'abc' []}} {{using page}}[]default page argument {{/using}} {{/include}} ")
    page_check (' {{require para/}} {{require next/}} body text', "[]{{require 'next'/}}{{require 'para'/}} body text")
    page_check (' {{require pageName}} default page value {{/require}} page text ', "[]{{require 'pageName'}} []default page value  {{/require}} page text ")
    page_check ('{{id/}}', '[]{{id/}}')
    page_check ('{{id name/}}', "[]{{id 'name'/}}")
    page_check ('{{get-cgi name/}}', "[]{{get-cgi 'name'/}}")
    page_check ('{{cgi-default name}} some stuff {{id/}} {{/cgi-default}}', '[]{{cgi-default name}}[]some stuff {{id/}}{{/cgi-default}}')
    page_check ('{{include "abc"}} {{set-cgi name}}value{{/set-cgi}}{{/include}}', u"[]{{include 'abc' []}} {{set-cgi name}}[]value{{/set-cgi}}{{/include}}")
    page_check ('{{cgi-default name}} {{get-cgi othername/}} {{/cgi-default}}', "[]{{cgi-default name}}[]{{get-cgi 'othername'/}}{{/cgi-default}}")
    page_check('{{get-env nonexistant}}default value{{/get-env}}')
    
    print "page tests complete with no exceptions"

if __name__=="__main__":
    print "because of import circularity issues parseTemplate tests must be launched from another module"
    #json_test()
    #page_test()
    #page_fail_test()
    #print "SUCCESS: tests complete with no exception"
