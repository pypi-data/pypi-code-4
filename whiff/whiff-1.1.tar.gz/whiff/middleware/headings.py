"""
Collect headings in text into a list in the environment.
Use the headingsFormat to format the headings.

This is to be used in collaboration with the "heading" middleware.
"""

whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/headings - collect headings and format index
{{/include}}

The <code>whiff_middleware/headings</code>
middleware collects the headers declared using the
<code>heading</code> heading middleware and uses
the <code>headingsFormat</code> argument to format
an index.

"""

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv

headingListName = "whiff.middleware.headingList"

class headings(misc.utility):
    def __init__(self,
               headingsFormat, # formatter for collected headings
               text, # text containing headings
               variable=headingListName, # environment variable name for heading list collector
               ):
        self.headingsFormat = headingsFormat
        self.text = text
        self.variable = variable
    def __call__(self, env, start_response):
        variable = self.param_value(self.variable, env)
        # set up the list collector
        env = env.copy()
        env[variable] = [] # this must be done explicitly in the container environment
        # execute the text (which should populate the collector)
        text = self.param_value(self.text, env)
        # CONVENTION: if the header has fewer than two entries delete it
        if len(env[variable])<2:
            del env[variable]
        # use the populated environment to format the headers
        headers = self.param_value(self.headingsFormat, env)
        # deliver the page catenating the headers and text
        return self.deliver_page(headers+text, env, start_response)

__middleware__ = headings
