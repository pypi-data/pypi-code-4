
"""
switch on string cases
"""

whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/switch - switch on string cases
{{/include}}

The <code>whiff_middleware/switch</code>
middleware delivers the page whose <code>case_</code>
name matches the <code>value</code>

{{include "example"}}
{{using targetName}}switch{{/using}}
{{using page}}

{{include "whiff_middleware/switch"}}
    {{using value}}{{get-env REQUEST_METHOD/}}{{/using}}
    {{using case_GET}}
        GET HTTP request:
        You sent a simple URL request with no data in the
        request body.
    {{/using}}
    {{using case_POST}}
        POST HTTP request:
        You sent a request which may have data in the
        request body.
    {{/using}}
    {{using default}}
        {{get-env REQUEST_METHOD/}} request:
        neither a POST or GET. I can't comment on this one.
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

# import must be absolute
from whiff.middleware import misc

class switch(misc.utility):
    def __init__(self,
                 value,
                 default=None,
                 **cases):
        # all cases should be named case_*
        for (n, v) in cases.items():
            if not n.startswith("case_"):
                raise NameError, "illegal argument for switch "+repr(n)
        self.value = value
        self.cases = cases
        self.default = default
    def __call__(self, env, start_response):
        value = self.param_value(self.value, env).strip()
        case_name = "case_"+value
        cases = self.cases
        page = cases.get(case_name, self.default)
        if page is None:
            raise ValueError, "no such case provided "+repr(case_name)
        # let the page start the response
        pagevalue = self.param_value(page, env, start_response)
        return [pagevalue]

__middleware__ = switch

def test():
    env = {}
    app = switch("a", case_a="a value", case_b="b value", default="default value")
    print "test of switch should say 'a value'", app(env, misc.ignore)
    app = switch("b", case_a="a value", case_b="b value", default="default value")
    print "test of switch should say 'b value'", app(env, misc.ignore)
    app = switch("c", case_a="a value", case_b="b value", default="default value")
    print "test of switch should say 'default value'", app(env, misc.ignore)

if __name__=="__main__":
    test()
