"""
Simple conditional based on page value: test if all white or not
"""

whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/ifVisible - test presence  of visible text
{{/include}}

The <code>whiff_middleware/ifVisible</code>
middleware tests whether a test page contains
visible text.  If it does deliver the <code>page</code>
argument. If the test page is all white deliver the
<code>elsePage</code>.

{{include "example"}}
{{using targetName}}ifVisible{{/using}}
{{using page}}

{{include "whiff_middleware/ifVisible"}}
{{using testPage}} {{get-env usesWhiteDefaultValue}} {{/get-env}} {{/using}}
    {{using page}} The test page is visible. {{/using}}
    {{using elsePage}}The test page is not visible.{{/using}}
{{/include}}

{{/using}}
{{/include}}
"""

from whiff.middleware import misc

class ifVisible(misc.utility):
    def __init__(self,
                 testPage,
                 page,
                 elsePage="", # page to deliver if testpage is all white
                 ):
        self.testPage = testPage
        self.page = page
        self.elsePage = elsePage
    def __call__(self, env, start_response):
        test = self.param_value(self.testPage, env).strip() 
        if test:
            return self.deliver_page(self.page, env, start_response)
        else:
            return self.deliver_page(self.elsePage, env, start_response)

__middleware__ = ifVisible
