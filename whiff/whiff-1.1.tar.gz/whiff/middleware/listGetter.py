
"""
getter middleware for use with loadList to get data from a list of strings
"""

whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/listGetter - get values from a list for dropdown
{{/include}}

The <code>whiff_middleware/listGetter</code>
middleware is a <em>getter</em> for use with
<code>loadList</code> which gets values from
a <code>data</code> sequence.

"""

from whiff.rdjson import jsonParse
from whiff.middleware import misc

class listGetter(misc.utility):
    def __init__(self, prefix,
                 data, # this sequence to index
                 matchValue="",
                 index=None,
                 style="jswhiff_suggestionItem",
                 ):
        self.prefix = prefix
        self.data = data
        self.matchValue = matchValue
        self.index = index
        self.style = style
    def __call__(self, env, start_response):
        index = self.param_json(self.index, env)
        data = self.param_json(self.data, env)
        matchValue = self.param_value(self.matchValue, env)
        prefix = self.param_value(self.prefix, env)
        style = self.param_value(self.style, env)
        # derive index from match value
        if matchValue:
            count = 0
            for v in data:
                if v.startswith(matchValue):
                    index = count
                count += 1
        if index is None:
            index = 0
        identifier = "%s_%s"%(prefix, index)
        # raise IndexError if done
        value = data[index]
        format = '<span id="%s" class="%s"> %s </span>' % (identifier, style, value)
        action = None
        D = {}
        D["format"] = format
        D["value"] = value
        D["action"] = action
        D["index"] = index
        D["id"] = identifier
        start_response("200 OK", [('Content-Type', 'application/javascript')])
        yield jsonParse.format(D)                                                        

__middleware__ = listGetter
