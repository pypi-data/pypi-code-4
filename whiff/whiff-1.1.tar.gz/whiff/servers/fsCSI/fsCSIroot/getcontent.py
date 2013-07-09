
from whiff.middleware import misc
from whiff import gateway

class getcontent(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        path = self.param_value(self.page, env)
        resourcePathList = ["content", path]
        resourceValue = gateway.getResource(env, resourcePathList)
        return self.deliver_page(resourceValue, env, start_response)

__middleware__ = getcontent
