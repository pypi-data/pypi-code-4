
"""
Format dictionary using a page.
"""

whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/format - format a string using a dictionary
{{/include}}

The <code>whiff_middleware/format</code>
middleware fills in locations in a string using
values from a mapping.  The string substitution
format is implemented using the standard Python
<code>string%dictionary</code> format conventions.

{{include "example"}}
{{using targetName}}format{{/using}}
{{using page}}

{{include "whiff_middleware/format"}}
    {{using page}}
        The %(gender)s %(name)s is %(age)d years old and
        %(height)4.2f meters tall.
    {{/using}}
    {{using dictionary}}
        {
        "gender": "girl",
        "age": 5,
        "name": "sally",
        "height": 1.234443,
        "room": "432B"
        }
    {{/using}}
{{/include}}

{{/using}}
{{/include}}
"""

import types

# import must be absolute
from whiff.middleware import misc

class format(misc.utility):
    def __init__(self,
                 page, # page format to use
                 dictionary=None, # dictionary to format
                 datavariable=None, # environment variable containing the dictionary
                 ):
        #pr "repeat", (page, dictionary, datavariable)
        if datavariable is None and dictionary is None:
            raise ValueError, "no data source specified: need datavariable or dictionary"
        if datavariable is not None and dictionary is not None:
            raise ValueError, "ambiguous data source: need exactly one of datavariable or dictionary"
        self.datavariable = datavariable
        self.dictionaryData = dictionary
        self.page = page
    def __call__(self, env, start_response):
        # determine the dictionary
        dictionary = self.dictionaryData
        #pr "got dictionary", repr(dictionary)
        if dictionary is None:
            #pr "getting data from env"
            datavariable = self.param_value(self.datavariable, env).strip()
            dictionary = env[datavariable]
        #pr "dictionary before json conversion"
        #pr dictionary
        d = self.param_json(dictionary, env)
        #pr "dictionary as json"
        #pr dictionary
        if type(d) in types.StringTypes:
            raise ValueError, "format requires a dictionary argument"
        # allow the page to start the response
        pageText = self.param_value(self.page, env, start_response)
        substitutedText = pageText % d
        return [substitutedText]

__middleware__ = format

def test():
    env = {}
    def page(env, start_response):
        start_response("200 OK", [('Content-Type', 'image/png')])
        yield " x = %(x)s and y = %(y)s "
    D = { "x": "THE X VALUE", "y": 42 }
    app = format(page, D)
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "::test of format got result"
    print result
    print "::end of test result"

if __name__=="__main__":
    test()
