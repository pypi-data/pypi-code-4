
"""
Simple conditional based on environment entry.

Test whether variable is defined and non-false
"""

whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/ifdef - test presence of environment variable
{{/include}}

The <code>whiff_middleware/ifdef</code>
middleware tests whether an environment variable
is present or absent and delivers the page
argument only if the variable is present.
If the variable is absent <code>ifcgi</code>
delivers the <code>elsePage</code> argument
or an empty string if the <code>elsePage</code>
is not specified.  An environment variable with a value
which tests false
is considered to be absent.

{{include "example"}}
{{using targetName}}ifdef{{/using}}
{{using page}}

{{include "whiff_middleware/ifdef"}}
    {{using variable}}NoSuchEnvVariable{{/using}}
    {{using page}}NoSuchEnvVariable={{get-env NoSuchEnvVariable/}}{{/using}}
    {{using elsePage}}NoSuchEnvVariable is not defined.{{/using}}
{{/include}}

{{/using}}
{{/include}}
"""

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv

class ifdef(misc.utility):
    def __init__(self,
                 page, # page to deliver if found
                 variable=None, # environment variable to test for (default: look for whiffenv.NAME in env)
                 elsePage="", # page to deliver if not found
                 ):
        self.variable = variable
        self.ifFoundPage = page
        self.notFoundPage = elsePage
    def __call__(self, env, start_response):
        variable = self.param_value(self.variable, env)
        if variable:
            variable = variable.strip()
        if not variable:
            # look in environment
            variable = whiffenv.getName(env) #env.get(whiffenv.NAME)
            if not variable:
                raise ValueError, "ifdef: variable not specified and %s not found in environment" % (whiffenv.NAME,)
            variable = variable.strip()
        #pr "IFDEF TESTING VAR", variable
        #test = (env.get(variable) is not None)
        test = env.get(variable)
        if test:
            #pr "VARIABLE FOUND AND NON-FALSE"
            return self.deliver_page(self.ifFoundPage, env, start_response)
        else:
            #pr "VARIABLE NOT FOUND OR SET FALSE"
            return self.deliver_page(self.notFoundPage, env, start_response)

__middleware__ = ifdef

def test():
    env = { "testvar": "present" }
    app = ifdef(variable="testvar", page="right page", elsePage="WRONG PAGE")
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "test GOT", repr(result)
    env = { "wrongvar": "present" }
    app = ifdef(variable="testvar", page="WRONG PAGE", elsePage="right page")
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "print GOT", repr(result)
    env = { "wrongvar": "present", whiffenv.NAME: "testvar2" }
    app = ifdef(page="WRONG PAGE", elsePage="right page")
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "print GOT", repr(result)

if __name__=="__main__":
    test()
