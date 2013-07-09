
"""
Simple repetition over sequence
"""

whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/repeat - repeat page for each element of sequence
{{/include}}

The <code>whiff_middleware/repeat</code>
middleware iterates over each element of its <code>sequence</code>
argument, generating the <code>page</code> argument for each iteration.
the sequence element will be set to the environment entry named
by the <code>variable</code> argument.  If the sequence variable is
not provided and the <code>datavariable</code> argument is defined
the middleware will use the environment entry named by the environment
entry named by
<code>datavariable</code> 

{{include "example"}}
{{using targetName}}repeat{{/using}}
{{using page}}

<table border>
{{include "whiff_middleware/repeat"}}
    {{using sequence}} ["one", "two", "buckle my shoe"] {{/using}}
    {{using variable}} line {{/using}}
    {{using page}}
        <tr><td bgcolor="#5588aa"> {{get-env line/}}
        </td></tr>
    {{/using}}
{{/include}}
</table>

{{/using}}
{{/include}}

"""
import types

# import must be absolute
from whiff.middleware import misc

class repeat(misc.utility):
    def __init__(self,
                 variable, # environment variable to store the current entry value
                 page, # page to repeat
                 sequence=None, # sequence to iterate over (data element!)
                 datavariable=None, # environment variable containing the sequence
                 defaultvalue=None, # default json value if env var is absent
                 ):
        #pr "repeat", (variable, page, sequence, datavariable)
        if datavariable is None and sequence is None:
            raise ValueError, "no data source specified: need datavariable or sequence"
        if datavariable is not None and sequence is not None:
            raise ValueError, "ambiguous data source: need exactly one of datavariable or sequence"
        self.variable = variable
        self.datavariable = datavariable
        self.sequenceData = sequence
        #pr "set sequence", (sequence, self.sequenceData)
        self.page = page
        self.defaultvalue = defaultvalue
    def __call__(self, env, start_response):
        variable = self.param_value(self.variable, env)
        variable = variable.strip()
        # determine the sequence
        sequence = self.sequenceData
        #pr "got sequence", (sequence, self.sequenceData)
        if sequence is None:
            #pr "getting data from env"
            datavariable = self.param_value(self.datavariable, env).strip()
            #pr "got", sequence
            if env.has_key(datavariable):
                sequence = env[datavariable]
            elif self.defaultvalue:
                sequence = self.param_json(self.defaultvalue, env)
            else:
                raise KeyError, "no such environment entry "+repr(datavariable)
        #pr "repeating", datavariable
        #pr "sequence before json conversion"
        #pr sequence
        sequence = self.param_json(sequence, env)
        #pr "sequence as json"
        #pr sequence
        if type(sequence) in types.StringTypes:
            raise ValueError, "repeat refuses to iterate over strings, use list of char instead"
        responses = []
        for value in sequence:
            new_env = env.copy()
            new_env[variable] = value
            resp = self.param_value(self.page, new_env)
            responses.append(resp)
        # always return text/plain 
        # ancestor must override content-type
        headers = self.derive_headers('text/plain')
        start_response("200 OK", headers)
        for resp in responses:
            yield resp

__middleware__ = repeat

def test():
    env = {}
    def page(env, start_response):
        start_response("200 OK", [('Content-Type', 'image/png')])
        yield "env = "+repr(env)+"\n"
    app = repeat("VARIABLE", page, ["FIRST", "SECOND", "THIRD", "LAST"])
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "::test of repeat got result"
    print result
    print "::end of test result"

if __name__=="__main__":
    test()
