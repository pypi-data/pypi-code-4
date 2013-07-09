
"""
Remove an entry from the environment and call page with modified environment
"""

whiffCategory = "naming"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/undef - undefine an environment entry for page
{{/include}}

The <code>whiff_middleware/undef</code>
middleware "hides" an environment entry from its page argument,
evaluating the page (and its components recursively)
with a modified environment which does not contain the environment
entry.

{{include "example"}}
{{using targetName}}undef{{/using}}
{{using page}}

{{include "whiff_middleware/undef"}}
    {{using variable}}REMOTE_ADDR{{/using}}
    {{using page}}
        inside your addr is: {{get-env REMOTE_ADDR}}*unknown*{{/get-env}} <BR>
    {{/using}}
{{/include}}
but outside your addr is: {{get-env REMOTE_ADDR}}*unknown*{{/get-env}} <BR>

{{/using}}
{{/include}}

"""
# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv

class undef(misc.utility):
    def __init__(self, page, variable=None):
        self.page = page
        self.variable = variable # variable to undefine (default: use whiffenv.NAME)
    def __call__(self, env, start_response):
        variable = self.param_value(self.variable, env)
        if variable:
            variable = variable.strip()
        if not variable:
            # look for NAME in env
            variable = whiffenv.getName(env)
            if not variable:
                raise ValueError, "undef: variable not specified and and %s not found in environment" % (whifenv.NAME,)
            variable = variable.strip()
        envcopy = env.copy()
        assert variable!=whiffenv.RPC_TAINTED, "unsetting rpc taint mark is not permitted as a security precaution"
        try:
            del envcopy[variable]
        except KeyError:
            # ignore absent entry ?
            pass
        return self.deliver_page(self.page, envcopy, start_response)
                
__middleware__ = undef

def test():
    # basic code exercise, doesn't verify logic
    ud = undef("dummy page", "x")
    out = ud({"x":"y"}, misc.ignore)
    print "test of undef gets", list(out)

if __name__=="__main__":
    test()

