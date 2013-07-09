
from whiff import whiffenv
from whiff.middleware import misc

class Prepare(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        """
        correlate data from the cgi parameters with data from the query results.
        """
        start = stop = ""
        any = ""
        env = env.copy()
        results = whiffenv.getId(env, "results")
        if not results:
            raise ValueError, "results environment entry missing"
        (ids, completions, suggestions) = results
        completions = completions[:30] # only keep up to 30 completions
        cgi = env.get(whiffenv.CGI_DICTIONARY)
        if cgi is None:
            raise ValueError, "cgi dictionary not yet parsed"
        NameToAttInfo = {}
        for (name, values) in cgi.items():
            if name=="_submit":
                pass
            elif name=="_start":
                start = values[0]
            elif name=="_stop":
                stop = values[0]
            elif name=="_any":
                any = values[0]
            else:
                for value in values:
                    D = NameToAttInfo.get(name, {})
                    D["value"] = value
                    D["suggestions"] = []
                    NameToAttInfo[name] = D
        for (name, suggestionList) in suggestions:
            D = NameToAttInfo.get(name, {})
            D["suggestions"] = suggestionList[:20] # only keep 20 suggestions
            D["value"] = D.get("value", "")
            NameToAttInfo[name] = D
        # throw out empty suggestions
        for (name, D) in NameToAttInfo.items():
            if not D.get("suggestions"):
                del NameToAttInfo[name]
        Attinfo = NameToAttInfo.items()
        Attinfo.sort()
        whiffenv.setId(env, "attInfo", Attinfo)
        whiffenv.setId(env, "completions", completions)
        whiffenv.setId(env, "ids", ids)
        whiffenv.setId(env, "start", start)
        whiffenv.setId(env, "stop", stop)
        whiffenv.setId(env, "any", any)
        return self.deliver_page(self.page, env, start_response)

__middleware__ = Prepare
