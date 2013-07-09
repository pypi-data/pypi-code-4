
whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/unauthorized - return "unauthorized" response
{{/include}}

The <code>whiff_middleware/unauthorized</code>
sends an HTTP response telling the client that
the request cannot be answered as requested because
the client is not authorized to access the resource.

"""
from whiff.middleware import misc

class unauthorized(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        def my_start_response(status, headers):
            if status<"401":
                status = "401 unauthorized"
            return start_response(status, headers)
        #return self.page(env, my_start_response)
        return self.deliver_page(self.page, env, my_start_response)

__middleware__ = unauthorized
