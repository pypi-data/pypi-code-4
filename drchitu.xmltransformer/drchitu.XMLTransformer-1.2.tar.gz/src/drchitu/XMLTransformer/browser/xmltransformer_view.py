from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import zlib, cPickle, base64


class XMLTransformerView(BrowserView):

    template = ViewPageTemplateFile('xmltransformer.pt')
    licenseTemplate = ViewPageTemplateFile('xmltransformer_license.pt')

    license = "eNprYIotZAxl1ErUAwAOPAJh"

    def get_hostname(self, request):
        """ Extract hostname in virtual-host-safe manner

        @param request: HTTPRequest object, assumed contains environ dictionary

        @return: Host DNS name, as requested by client. Lowercased, no port part.
                 Return None if host name is not present in HTTP request headers
                 (e.g. unit testing).
        """

        if "HTTP_X_FORWARDED_HOST" in request.environ:
            # Virtual host
            host = request.environ["HTTP_X_FORWARDED_HOST"]
        elif "HTTP_HOST" in request.environ:
            # Direct client request
            host = request.environ["HTTP_HOST"]
        else:
            return None

        # separate to domain name and port sections
        host=host.split(":")[0].lower()

        return host

    def is_licensed_host(self, request):
        try:
            hosts = self.zbPickleload(self.license)
            if (self.get_hostname(request) in hosts or '*' in hosts):
                return True
        except:
            print 'Error loading the license. Please check the installation integrity.'
            return False
        return False

    def zbPickledump(self, obj):
      return base64.encodestring(zlib.compress(cPickle.dumps(obj,cPickle.HIGHEST_PROTOCOL),9))

    def zbPickleload(self, zstr):
      return cPickle.loads(zlib.decompress(base64.decodestring(zstr)))  


    def __call__(self):
        """"""
        # self.hello_name = getattr(self.context, 'hello_name', 'World')i
        if (self.is_licensed_host(self.request)):
            return self.template()
        return self.licenseTemplate()
