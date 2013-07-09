
"""
Simple conditional based on cgi variable presence or absence
"""

whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/ifcgi - test presence of cgi variables
{{/include}}

The <code>whiff_middleware/ifcgi</code>
middleware tests whether all
listed CGI form variables
are present or absent and delivers the page
argument only if the variables are present.
If any of the variable are absent <code>ifcgi</code>
delivers the <code>elsePage</code> argument
or an empty string if the <code>elsePage</code>
is not specified.  A CGI variable with a value
which consists of only whitespace or an empty string
is considered to be absent.

{{include "example"}}
{{using targetName}}ifcgi{{/using}}
{{using page}}

{{include "whiff_middleware/ifcgi"}}
    {{using variables}}NoSuchCGIVariable{{/using}}
    {{using page}}Thank you for providing a value for NoSuchCGIVariable{{/using}}
    {{using elsePage}}The form entry NoSuchCGIVariable is required{{/using}}
{{/include}}

{{/using}}
{{/include}}
"""

# import must be absolute
from whiff.middleware import misc
from whiff import resolver
from whiff import whiffenv

class ifcgi(misc.utility):
    def __init__(self,
                 variables, # cgi variable to test for
                 page, # page to deliver if found
                 elsePage="", # page to deliver if not found
                 ):
        self.variables = variables #self.param_text(variables).split()
        self.ifFoundPage = page
        self.notFoundPage = elsePage
    def __call__(self, env, start_response):
        variables = self.param_value(self.variables, env).split()
        env = resolver.process_cgi(env, parse_cgi=True)
        cgi_parameters = env[whiffenv.CGI_DICTIONARY]
        test = True
        for v in variables:
            value = cgi_parameters.get(v)
            if value is None:
                test = False
                break
            if value[0].strip()=="":
                test = False
                break
        if test:
            #pr "require", v, "found", cgi_parameters
            #pr "delivering", self.ifFoundPage
            result = list( self.deliver_page(self.ifFoundPage, env, start_response))
            #pr "result is"
            #pr repr("".join(result))
            return result
        else:
            #pr "require", v, "not found", cgi_parameters
            result = list(self.deliver_page(self.notFoundPage, env, start_response))
            return result

__middleware__ = ifcgi

