from collective.editmodeswitcher.config import COOKIE_NAME


def set_editmode(site, event):
    """Event handler which disables borders if the according cookie is set.
    """
    request = event.request
    if request.cookies.get(COOKIE_NAME, '') == '1':
        request.set('disable_border', 1)
