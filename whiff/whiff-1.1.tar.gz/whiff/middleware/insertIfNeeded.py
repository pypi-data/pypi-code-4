
"""
Add a chunk of text (javascript) if it hasn't been added already.
"""

whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/insertIfNeeded - insert a text only once, if needed
{{/include}}

The <code>whiff_middleware/insertIfNeeded</code>
middleware is a mechanism to make sure that a segment
of text (like a javascript function) are only introduced
once.  It uses local resources to indicate whether
the text is already inserted or whether the text is
needed.


{{include "example"}}
{{using targetName}}insertIfNeeded{{/using}}
{{using page}}

{{include "whiff_middleware/insertIfNeeded"}}
    {{using text}} <HR> INSERT ME ONCE ONLY <HR> {{/using}}
    {{using doneFlag}} ["local", "insertOnceFlag"] {{/using}}
{{/include}}

{{include "whiff_middleware/insertIfNeeded"}}
    {{using text}} <HR> INSERT ME ONCE ONLY <HR> {{/using}}
    {{using doneFlag}} ["local", "insertOnceFlag"] {{/using}}
{{/include}}

{{include "whiff_middleware/insertIfNeeded"}}
    {{using text}} <HR> INSERT ME ONCE ONLY <HR> {{/using}}
    {{using doneFlag}} ["local", "insertOnceFlag"] {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

from whiff.middleware import misc
from whiff import gateway
from whiff import whiffenv

class insertIfNeeded(misc.utility):
    def __init__(self,
                 text,
                 doneFlag, # if this local resource is set then don't insert text, set after insert
                 needFlag=None, # if defined insert the text only if the local resource is set
                 ):
        self.text = text
        self.doneFlag = doneFlag
        self.needFlag = needFlag
    def __call__(self, env, start_response):
        doneFlag = self.param_value(self.doneFlag,env)
        donePath = ["local", doneFlag]
        done = gateway.getResource(env, donePath, False)
        if not done:
            needed = True
            if self.needFlag:
                needFlag = self.param_value(self.needFlag, env)
                needPath = ["local", needFlag]
                needed = gateway.getResource(env, needPath, False)
            if needed:
                # the text is needed and not done: mark it as done and deliver the text
                gateway.putResource(env, donePath, True)
                return self.deliver_page(self.text, env, start_response)
        # if we get here, don't do anything and deliver empty string
        return self.deliver_page("", env, start_response)

__middleware__ = insertIfNeeded
