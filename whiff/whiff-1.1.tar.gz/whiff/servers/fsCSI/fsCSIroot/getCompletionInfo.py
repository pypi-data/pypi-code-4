
from whiff import resolver
from whiff import whiffenv
from whiff.middleware import misc
from whiff import gateway
from whiff.rdjson import jsonParse

def completeValue(v, matches):
    v = v.strip()
    if not v:
        return matches
    s = v.split()
    lastword = s[-1].lower()
    prefix = " ".join(s[:-1])
    if prefix:
        prefix += " "
    resultD = {}
    for M in matches:
        m = M.lower()
        if m.startswith(lastword):
            resultD[prefix+M] = 1
    result = resultD.keys()
    result.sort()
    return result

def debugDump(cgi, output, filename="/tmp/debug0.txt"):
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
        filteredValue.append(resourceValue[0])
        filteredValue.append(generalMatches)
        debugDump(cgiDict, filteredValue)
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        yield "completionInfo = "
        yield jsonParse.format(filteredValue)
        yield ";\n"
        yield "callBackActive = false;\n"
        yield "debugReport('ajax response');"

__middleware__ = getCompletionInfo
