
whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/Eval -- expand string as template
{{/include}}

The <code>whiff_middleware/Eval</code>
middleware is useful for implementing AJAX-type functionality.
It interprets its string argument as a template and expands the
template, returning the expansion.

{{include "example"}}

{{include "whiff_middleware/Eval"}}
      {${include "whiff_middleware/debugDump"/}$}
{{/include}}

{{/include}}      
Since the evaluated string may include substrings
which may have been submitted by remote agents
the string argument is evaluated in a copy of the
current WHIFF environment marked as RPC tainted as a
security precaution.
The RPC tainted environment prevents the evaluated template
from executing unsafe operations such as evaluating
Mako templates (which may include arbitrary Python code).
"""
from whiff.middleware import misc
from whiff import parseTemplate
from whiff import resolver
from whiff import whiffenv
import expandPostedTemplate

class Eval(misc.utility):
    def __init__(self,
                 page,
                 relativeUrl = None,
                 ):
        self.page = page
        self.relativeUrl = relativeUrl
    def __call__(self, env, start_response):
        # as a security precaution mark the environment as tainted
        env = whiffenv.mark_rpc_tainted(env)
        page = self.param_value(self.page, env)
        #pr "evalling page of len", len(page)
        (test, result, cursor) = parseTemplate.parse_page(page, file_path="[Eval argument: %s...]" % repr(page.strip()[:80]))
        if not test:
            c1 = page[ max(0, cursor-20): cursor ]
            c2 = page[ cursor : cursor+20 ]
            raise ValueError, "Eval template parse for payload reports error "+repr((result, cursor, c1, c2))
        stream = result.makeWsgiComponent()
        root_application = env[whiffenv.ROOT] # self.whiff_root_application
        responding_path = env[whiffenv.RESPONDING_PATH] # self.whiff_responding_path
        path_remainder = env[whiffenv.PATH_REMAINDER] # self.whiff_path_remainder
        outer_arguments = {} # self.whiff_outer_arguments
        # if the relative URL is provided, adjust the environment, and stream binding
        if self.relativeUrl is not None:
            relativeUrl = self.param_value(self.relativeUrl, env)
            env = expandPostedTemplate.relativeEnvironment(env, relativeUrl)
            responding_path = relativeUrl.split("/")
            path_remainder = []
        stream.bind_root(root_application, responding_path, path_remainder, outer_arguments)
        evalOut = stream(env, start_response)
        return evalOut

__middleware__ = Eval
