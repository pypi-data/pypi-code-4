
whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/printMessage - print console message
{{/include}}

The <code>whiff_middleware/printMessage</code>
middleware 
prints a message to the standard
output and returns an empty result response.
"""

from whiff.middleware import misc

class printMessage(misc.utility): # verbose
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        message = self.param_value(self.page, env)
        print message # verbose print message to stdout (don't comment this line!)
        return self.deliver_page("", env, start_response)

__middleware__ = printMessage # verbose

def test():
    pm = printMessage("verbose test print should output")
    result = pm({}, misc.ignore)
    result = list(result)
    print "test of printMessage generated", result

if __name__=="__main__":
    test()
