"""
Format a heading and store the heading level and text in a list in the environment
(for possible formatting elsewhere).
"""

whiffCategory = "Tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/heading - create a heading cross reference
{{/include}}

The <code>whiff_middleware/heading</code>
middleware creates a heading entry in a page which
can be cross referenced with an index generated using
the <code>headings</code> middleware.

"""

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff.middleware import headings

headingLevelName = "whiff.middleware.headingLevel"

class heading(misc.utility):
    def __init__(self,
                 page, # the text of the heading
                 variable=headingLevelName,
                 listVariable=headings.headingListName,
                 ):
        self.page = page
        self.variable = variable
        self.listVariable = listVariable
    def __call__(self, env, start_response):
        variable = self.param_value(self.variable, env)
        listvariable = self.param_value(self.listVariable, env)
        page = self.param_value(self.page, env)
        headerList = env.get(listvariable)
        if headerList is None:
            headerList = []
        else:
            #headerList = list(headerList)
            pass
        headerName = whiffenv.getName(env, "Header%s" % len(headerList))
        headerLevel = int(env.get(variable, "3"))
        # record the level and the text of the header in the accumulator
        headerList.append( (headerLevel, headerName, page) )
        # store headerlist in case it's new
        env[listvariable] = headerList
        # deliver the header formatted as html
        headerText = '<h%s><a id="%s"></a>%s</h%s>' % (headerLevel, headerName, page, headerLevel)
        return self.deliver_page(headerText, env, start_response)

__middleware__ = heading
