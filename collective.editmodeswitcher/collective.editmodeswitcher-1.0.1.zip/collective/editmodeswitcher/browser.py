import time
from Products.Five import BrowserView
from Acquisition import aq_inner
from ZServer.medusa.http_date import build_http_date
from collective.editmodeswitcher.config import COOKIE_NAME, COOKIE_LIFETIME


class EditModeSwitcher(BrowserView):
    """A browser view for setting/deleting a cookie which disables edit mode
       (aka borders).
    """

    def __call__(self):
        """Delete the cookie if there's already one or create a new one if no
           cookie is present.
        """
        context = aq_inner(self.context)
        if self.request.get(COOKIE_NAME, '') == '1':
            self.request.response.expireCookie(COOKIE_NAME, path='/')
        else:
            self.request.response.setCookie(COOKIE_NAME, '1', path='/',
                expires=build_http_date(time.time() + COOKIE_LIFETIME))

        self.request.response.redirect(context.absolute_url(), status=302)
