from django.conf import settings
from django.template.defaultfilters import slugify
import os
import re

# http://www.useragentstring.com/pages/Mobile%20Browserlist/ + others
# KISS, I'm intentionally leaving all the obscure stuff that ships
# with other packages out. A 90% solution is good enough - if more
# should come up, it's easy to extend.
USER_AGENTS = [ 
    'Android',
    'BlackBerry',
    'Blazer',
    'Bolt',
    'Doris',
    'Dorothy',
    'Fennec',
    'GoBrowser',
    'IEMobile',
    'Iris',
    'Kindle',
    'MIB',
    'Maemo Browser',
    'Minimo',
    'Mobile',
    'NetFront',
    'Opera Mini',
    'Opera Mobi',
    'SEMC-Browser',
    'Skyfire',
    'SymbianOS',
    'TeaShark',
    'Teleca',
    'iPad',
    'iPhone',
    'iPod',
    'uZard',
    'uZard',
    ]

# Full website cookie name
SESSION_KEY_NAME = getattr(settings, 'SESSION_KEY_NAME', 'mobile:full-website')

pattern = re.compile('|'.join(USER_AGENTS))

class Mobile(object):
    def __init__(self, ua, match):
        self.user_agent = ua
        self.slug = slugify(match.group()).lower()


class MobileDetectorMiddleware(object):
    """
    Monkey patches the request and adds two attributes:

    * :attr:`request.is_mobile`, a boolean value indicating if the
      request came from a mobile user agent or not. 

    * :attr:`request.mobile`, a custom object providing more
      information about the current mobile user agent or ``None`` if
      :attr:`request.is_mobile` is ``False``

    """

    def process_request(self, request):
        result = pattern.search(request.META.get('HTTP_USER_AGENT', ''))
        if result:
            setattr(request, 'is_mobile', True)
            setattr(request, 'mobile', Mobile(request.META['HTTP_USER_AGENT'], result))
        else:
            setattr(request, 'is_mobile', False)
            setattr(request, 'mobile', None)
    
class MobileTemplateMiddleware(object):
    """
    Prepends a number of template names to the template response if a
    mobile request was detected. For example, if the original template
    was ``blog/post.html`` and the request happened on an Android
    device, the following template names are prepended to the :class:`TemplateResponse`:

    * ``blog/mobile/android/post.html``
    * ``blog/mobile/post.html``

    The device, in this case 'android' is created by slugifying the
    match in the user agent and then lowercasing it.

    """

    def process_template_response(self, request, response):
        assert hasattr(request, 'is_mobile'), "You must install the 'mob.middleware.MobileDetectorMiddleware'"
        
        if not request.is_mobile:
            return response

        if hasattr(request, 'session') and request.session.get(SESSION_KEY_NAME, False):
            return response

        if not isinstance(response.template_name, (list, tuple)):
            response.template_name = [response.template_name]

        def explode(template_name):
            path, filename = os.path.split(template_name)

            return [
                os.path.join(path, 'mobile', request.mobile.slug, filename),
                os.path.join(path, 'mobile', filename),
                template_name
                ]

        response.template_name = [
            # Gotta flatten the list of template names
            name
            for names in map(explode, response.template_name)
            for name in names
            ]

        return response
