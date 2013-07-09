
"""
{{include "whiff_middleware/heading"}}
whiff_middleware/addCommentsFromResource - add comments to a page from
WHIFF resource
{{/include}}

The <code>whiff_middleware/addCommentsFromResource</code>
is an example of how to extract form data from a page submission
and put that data into a WHIFF resource.  This example is used
to implement the "feedback" forms for the WHIFF documentation.
"""

whiffDoc = __doc__

# xxxx the comment to store should be explicitly passed in as a require.
#  in stead of implicitly passed in as a well known cgi-default.

# import must be absolute
from whiff.middleware import misc
from whiff.middleware import getResource
from whiff.middleware import putResource
from whiff import whiffenv
from whiff import resolver
from whiff.rdjson import jsonParse
from whiff import stream
import os.path
import time

defaultCommentsName = "addComments.comments"
defaultErrorName = "addComments.error"
defaultCountName = "addComments.count"

class addCommentsFromResource(misc.utility):
    def __init__(self,
                 resourcePath,
                 layout,
                 variable=defaultCommentsName,
                 error=''):
        self.resourcePath = resourcePath
        self.layout = layout
        self.variable = variable
        self.error = error
    def __call__(self, env, start_response):
        archivePath = self.param_value(self.resourcePath, env)
        archivePath = archivePath.strip()
        error = self.param_value(self.error, env)
        variable = self.param_value(self.variable, env)
        commentsName = whiffenv.getName(env, variable)
        countName = whiffenv.getName(env, defaultCountName)
        name = email = comment = None
        # get the current comments (list of dicts)
        (flag, comments, index) = self.getData(archivePath, env)
        #pr "from", archivePath
        #pr "retrieved", comments
        # try to get cgi parameters
        env = resolver.process_cgi(env, parse_cgi=True)
        env = env.copy() # env modified below
        cgi_parameters = env[whiffenv.CGI_DICTIONARY]
        names = cgi_parameters.get("Name")
        # if nosubmit is set then check, but don't record (yet).
        nosubmits = cgi_parameters.get("NoSubmit")
        if names:
            name = names[0]
            name = name.strip()[:80]
        emails = cgi_parameters.get("Email")
        if emails:
            email = emails[0]
            email = email.strip()[:200]
        cgi_comments = cgi_parameters.get("Comment")
        if cgi_comments:
            comment = cgi_comments[0]
            comment = comment.strip()[:4000]
            #comment = comment.replace("\n", "<br>\n")
        if not error and name and not comment:
            error = "please provide a comment"
        if not error and comment and not name:
            error = "please provide a name"
        if not error and comment and len(comment)<20:
            error = "comment too short, please expand"
        # if "Name" and "Comment" are both defined with no error then try to update the archive with a new comment
        if name and comment and not error and not nosubmits:
            # try to modify the archive
            # prepend the new data
            theTime = time.ctime()
            newdata = {"Name": name, "Email": email, "Comment": comment, "Time": theTime}
            newdata["REMOTE_ADDR"] = env.get("REMOTE_ADDR")
            newdata["seconds"] = time.time()
            #pr "storing", comments
            comments = list(comments) + [newdata]
            self.storeData(archivePath, comments, env)
            # drop the submitted data which has been stored so it doesn't show in the layout.
            cgi_parameters = cgi_parameters.copy()
            del cgi_parameters["Name"]
            del cgi_parameters["Comment"]
            if email:
                del cgi_parameters["Email"]
            env[whiffenv.CGI_DICTIONARY] = cgi_parameters
        if error:
            errorName = whiffenv.getName(env, defaultErrorName)
            #pr "flagging error", (errorName, error)
            env[errorName] = "Error recording comment: "+error
        # install the archive data in the environment
        env[commentsName] = comments
        env[countName] = len(comments)
        # deliver the page formatting the data
        return self.deliver_page(self.layout, env, start_response)

    def getData(self, resourcePath, env):
        getter = getResource.getResource(resourcePath)
        text = stream.mystr(self.param_value(getter, env).strip())
        if not text:
            text = "[]"
        try:
            return jsonParse.parseValue(text)
        except 'bogus':
            # some error in file (should check more specifically)
            return []

    def storeData(self, resourcePath, data, env):
        fmt = jsonParse.format(data)
        putter = putResource.putResource(value=fmt, path=resourcePath)
        dummy = self.param_value(putter, env)
        return dummy

__middleware__ = addCommentsFromResource
