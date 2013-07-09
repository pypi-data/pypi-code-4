
"""
Introduce an FCK editor input element. (requires FCKeditor http://www.fckeditor.net/).

Note: this implementation can generate values containing code injection attacks if you
  don't filter the output generated for evil tags and values.
"""

whiffCategory = "library"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/FCKInput -- embed an FCKEditor input element
{{/include}}

The <code>whiff_middleware/FCKInput</code>
middleware introduces an FCK editor
WYSIWYG input element. (requires FCKeditor http://www.fckeditor.net/)
This middleware will
work correctly only if the FCK python module is
installed.  The FCK editor
software and server pagers are not installed automatically.
To install the FCK components follow the instructions at
<a href="http://www.fckeditor.net/">http://www.fckeditor.net/</a>
{{include "footnote"}}
This implementation can generate values containing code
injection attacks if you
don't filter the output generated for evil tags and values
using the <code>TestSafeHtml</code> middleware or some other
method.
{{/include}}

{{include "example"}}
{{using targetName}}FCKInput{{/using}}
{{using page}}

{{include "whiff_middleware/FCKInput"}}
    {{using inputName}}sillySaying{{/using}}
    {{using basePath}}/{{/using}}
    {{using value}}silly saying...{{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

#import fckeditor # you must have the fck editor python support installed to use this module
from whiff.middleware import misc
import os
from whiff.rdjson import jsonParse

class FCKInput(misc.utility):
    def __init__(self,
                 inputName,
                 basePath,
                 value = ""):
        self.inputName = inputName
        self.basePath = basePath
        self.value = value
    def __call__(self, env, start_response):
        # catch errors in fck library
        try:
            inputName = self.param_value(self.inputName, env).strip()
            basePath = self.param_value(self.basePath, env).strip()
            if basePath[-1:]!="/":
                basePath+="/"
            value = self.param_value(self.value, env)
            import fckeditor # you must have the fck editor python support installed to use this module
            oFCKeditor = fckeditor.FCKeditor(inputName)
            oFCKeditor.BasePath = basePath
            oFCKeditor.Height = "300" # this should be a require!
            oFCKeditor.Value = value
            # hack around a bug in fck python library: need to put the user agent in os.environ
            # XXX this hack is not safe for multi threaded servers (theoretically)... need to lock on os.env
            os_environ = os.environ
            new_os_env = os_environ.copy()
            new_os_env.update(env)
            try:
                os.environ = new_os_env
                frameOut = oFCKeditor.Create()
            finally:
                # restore the old os.environ
                os.environ = os_environ
        except:
            start_response("200 OK", [('Content-Type', 'text/html')])
            return ["<hr>fckeditor error<hr>"]
        else:
            start_response("200 OK", [('Content-Type', 'text/html')])
            D = {}
            D["jsonFrame"] = jsonParse.format(frameOut)
            D["name"] = inputName
            D["rows"] = 20
            D["cols"] = 50
            D["body"] = value
            htmlOut = TEMPLATE % D
            return [htmlOut]

TEMPLATE = """
<script>
document.write(%(jsonFrame)s);
</script>
<noscript>
<textarea name="%(name)s" rows="%(rows)s" cols="%(cols)s">%(body)s</textarea>
</noscript>
"""

__middleware__ = FCKInput

def test():
    env = {
        "HTTP_USER_AGENT":
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X; en-US; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14"
        }
    f = FCKInput("INPUTNAME", "/MY/BASE/PATH", "THE <EM>HTML</EM> VALUE TO START WITH")
    r = f(env, misc.ignore)
    print "test result"
    print "".join(list(r))

if __name__=="__main__":
    test()
