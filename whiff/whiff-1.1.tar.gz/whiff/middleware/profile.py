"""
get profiling information and put the text into a resource.
"""

whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/profile - store profile report for page generation
{{/include}}

The <code>whiff_middleware/profile</code>
middleware evaluates the <code>page</code> argument
while collecting profile information, storing the
resulting information in the <code>resourcePath</code>
(which defaults to <code>["local", "profile"]</code>).

{{include "example"}}
{{using targetName}}profile{{/using}}
{{using page}}

{{include "whiff_middleware/profile"}}
    {{using page}}
       test of profile:
       <pre> {{include "whiff_middleware/debugDump"/}} </pre>
    {{/using}}
{{/include}}

<h2>Profile report</h2>

<pre> {{include "whiff_middleware/getResource"}} ["local", "profile"] {{/include}} </pre>

{{/using}}
{{/include}}
"""

# xxxx needs to be featurized to support more cProfile bells and whistles

from whiff.middleware import misc
from whiff import gateway

class profile(misc.utility):
    def __init__(self,
                 page, # page to profile
                 resourcePath=["local", "profile"], # resource to receive the profile report
                 ):
        self.page = page
        self.resourcePath = resourcePath
    def __call__(self, env, start_response):
        import cProfile, pstats, StringIO
        resourcePath = self.param_json(self.resourcePath, env)
        prof = cProfile.Profile()
        D = {}
        D["self"] = self
        D["env"] = env
        stmt = "page = self.param_value(self.page, env)"
        prof = prof.runctx(stmt, D, D)
        page = D.get("page")
        assert page is not None, "self.param_value(self.page, env) failed to execute?"
        stream = StringIO.StringIO()
        stats = pstats.Stats(prof, stream=stream)
        stats.sort_stats("time")  # Or cumulative
        stats.print_stats(180)  # 80 = how many to print (verbose)
        #stats.print_callees() # verbose
        #stats.print_callers() # verbose
        report = stream.getvalue()
        gateway.putResource(env, resourcePath, report)
        return self.deliver_page(page, env, start_response)

__middleware__ = profile

