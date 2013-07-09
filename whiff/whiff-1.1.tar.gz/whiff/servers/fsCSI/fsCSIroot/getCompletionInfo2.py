
from whiff import resolver
from whiff import whiffenv
from whiff.middleware import misc
from whiff import gateway
from whiff.rdjson import jsonParse

def completeValue(v, matches, limit=10):
    v = v.strip()
    if not v:
        if limit:
            return matches[:limit]
        else:
            return matches
    s = v.split()
    lastword = s[-1].lower()
    prefix = " ".join(s[:-1])
    if prefix:
        prefix += " "
    resultD = {}
    for M in matches:
        if limit and len(resultD)>limit:
            break
        m = M.lower()
        if m.startswith(lastword):
            resultD[prefix+M] = 1
    result = resultD.keys()
    result.sort()
    return result

def debugDump(cgi, output, filename="/tmp/debug.txt"):
    f = open(filename, "w")
    f.write("cgi\n")
    f.write(jsonParse.format(cgi))
    f.write("\n\noutput\n")
    f.write(jsonParse.format(output))
    f.close()

class getCompletionInfo(misc.utility):
    def __call__(self, env, start_response):
        env = resolver.process_cgi(env, parse_cgi=True)
        # permit resource access
        env[whiffenv.RPC_TAINTED] = False
        cgiDict = env[whiffenv.CGI_DICTIONARY]
        completionResourcePath = ["index", "ids", cgiDict]
        resourceValue = gateway.getResource(env, completionResourcePath)
        filteredValue = []
        generalCompletions = resourceValue[1]
        generalValue = whiffenv.cgiGet(env, "_any", "")
        generalMatches = completeValue(generalValue, generalCompletions)
        filteredValue.append(resourceValue[0][:50])
        filteredValue.append(generalMatches)
        completionsDict = resourceValue[2]
        filteredDict = {}
        for (attrName, attrMatches) in completionsDict:
            attrValue = whiffenv.cgiGet(env, attrName, "")
            filteredMatches = completeValue(attrValue, attrMatches)
            filteredDict[attrName] = filteredMatches
        filteredValue.append(filteredDict)
        debugDump(cgiDict, filteredValue)
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        yield "completionsInfo = "
        yield jsonParse.format(filteredValue)
        yield ";\n"
        yield "callBackActive = false;\n"
        yield "processCompletionInfo();\n";
        yield "debugReport('ajax response');\n"

__middleware__ = getCompletionInfo
