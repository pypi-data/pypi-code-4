
whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/IfJavascriptUrl - internally redirect to URL only if javascript is enabled
{{/include}}

The <code>whiff_middleware/ifJavascriptUrl</code> provides support for handling browsers which have javascript disabled.
"""

whiffCategory = "logic"

# import must be absolute
from whiff.middleware import misc
from whiff import resolver
from whiff import whiffenv
from whiff import gateway

class ifJavascriptUrl(misc.utility):
    def __init__(self,
                 url,
                 elsePage="This page requires javascript"
                 ):
        self.url = url
        self.elsePage = elsePage
    def __call__(self, env, start_response):
        env = resolver.process_cgi(env, parse_cgi=True)
        url = self.param_value(self.url, env).strip()
        relative_url = env[whiffenv.TEMPLATE_PATH]
        javaScriptEnabled = whiffenv.cgiGet(env, "javaScriptEnabled", False)
        if javaScriptEnabled:
            return resolver.callUrl(url, env, start_response, relative_url)
        else:
            elsePage = self.param_value(self.elsePage, env)
            D = {}
            D["formname"] = gateway.getResource(env, ["freshName", "formname"])
            D["entry_point"] = env[whiffenv.ENTRY_POINT]
            D["elsePage"] = elsePage
            response = template % D
            return self.deliver_page(response, env, start_response)

template = """
<html>
<head>
<title> redirect page </title>
<script>
function onload_%(formname)s() {
document.getElementById("%(formname)s").submit();
}
</script>
</head>
<body onload="onload_%(formname)s()">

<form id="%(formname)s" method="post" action="%(entry_point)s">
<input type="hidden" name="javaScriptEnabled" value="true">
</form>

<noscript>
%(elsePage)s
</noscript>
</body>
"""

__middleware__ = ifJavascriptUrl
