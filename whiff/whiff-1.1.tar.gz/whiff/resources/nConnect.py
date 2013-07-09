"""
Get a nucular connection and deliver query results with suggestion dictionaries.

prefix + ["ids"] + query_data for ( ids, suggestions, suggestiondict )
prefix + ["dictionaries"] + query_data for ( dictionaries, suggestions, suggestiondict )

query data: list of
  ["start", start]
  ["stop", end]
  ["proximate", words]
  ["range", high, low]
  ["attword", attribute, word]
  etcetera (see below).
"""

import types
from nucular import Nucular # REQUIRES NUCULAR (SEPARATE INSTALL!)
from whiff.rdjson import jsonParse

class QueryError(ValueError):
    "query evaluation failed"

class Connection:
    def __init__(self, archiveDirectory):
        self.archiveDirectory = archiveDirectory
        self.session = None
    def getSession(self):
        session = self.session
        if session is None:
            #session = self.session = Nucular.Nucular(self.archiveDirectory, readOnly=True) # READONLY IS BROKEN!
            session = self.session = Nucular.Nucular(self.archiveDirectory, readOnly=False)
        return session
    def localize(self, env):
        "return a new finder to avoid thread interference issues"
        return Connection(self.archiveDirectory)
    def get(self, pathlist):
        assert len(pathlist)>=2, "expect indicator and data"
        (indicator, data) = pathlist
        session = self.getSession()
        if indicator=="ids":
            (query, result, ids, L, D) = self.queryForData(data)
            return (ids, L, D)
        elif indicator=="describe":
            result = session.describe(data)
            return result
        elif indicator=="results":
            (query, result, ids, L, D) = self.queryForData(data)
            if query is None:
                return [ [], [], [] ]
            resultObjects = [ result.describe(id) for id in ids ]
            resultDicts = [ ob.attrDict() for ob in resultObjects ] 
            return (resultDicts, L, D)
        elif indicator=="dictionaries":
            (query, result, ids, L, D) = self.queryForData(data)
            if query is None:
                return [ [], [], [] ]
            resultObjects = [ result.describe(id) for id in ids ]
            resultDicts = [ ob.asDictionary() for ob in resultObjects ] 
            return (resultDicts, L, D)
        else:
            raise ValueError, "unknown indicator "+indicator
    def queryForData(self, data):
        session = self.getSession()
        start = stop = None
        query = session.Query()
        for action in self.actionsForData(data):
            indicator = action[0]
            if indicator=="start":
                [start] = action[1:]
                start = int(start)
            elif indicator=="stop":
                [stop] = action[1:]
                stop = int(stop)
            elif indicator=="proximate":
                [words] = action[1:]
                words = words.strip()
                if words:
                    query.proximateWords(words, 3) # XXX hardcoded constant
            elif indicator=="range":
                [attribute, low, high] = action[1:]
                query.attributeRange(attribute, low, high)
            elif indicator=="match":
                [attribute, value] = action[1:]
                value = value.strip()
                if value:
                    query.matchAttribute(attribute, value)
            elif indicator=="prefix":
                [attribute, prefix] = action[1:]
                query.prefixAttribute(attribute, prefix)
            elif indicator=="attword":
                [attribute, word] = action[1:]
                query.attributeWord(attribute, word)
            elif indicator=="any":
                [word] = action[1:]
                query.anyWord(word)
            else:
                raise ValueError, "unknown action indicator "+repr(indicator)
        # now extract the ids...
        (R, status) = query.evaluate()
        if R is None:
            # return empty result
            return [None, None, [], [], [] ]
        ids = R.identities()
        if stop is not None:
            ids = ids[:stop]
        if start is not None:
            ids = ids[start:]
        # now extract the suggestions...
        (L, D) = query.suggestions(sampleSize=100)
        # linearize and sort the suggestions dictionary
        Ditems = []
        itm = D.items()
        itm.sort()
        for (attr, suggestions) in itm:
            suggestions = list(suggestions)
            suggestions.sort()
            Ditems.append((attr, suggestions))
        return (query, R, ids, L, Ditems)
    def actionsForData(self, data):
        td = type(data)
        if td is types.DictType:
            for (name, values) in data.items():
                if type(values) in types.StringTypes:
                    values = [values]
                for value in values:
                    if name=="_start":
                        yield ["start", value]
                    elif name=="_stop":
                        yield ["stop", value]
                    elif name=="_any":
                        yield ["any", value]
                    elif name.startswith("_"):
                        # ignore any other underscore name.
                        pass
                    else:
                        # otherwise its an attribute word restriction
                        yield ["attword", name, value]
        elif td is types.ListType or td is types.TupleType:
            for action in data:
                yield action
        else:
            raise ValueError, "don't know how to interpret data encoded as "+repr(td)
