from zaguan.engines import WebKitMethods, QTWebKitMethods
from zaguan.functions import asynchronous_gtk_message, get_implementation


implementation_name = get_implementation()


def launch_browser(uri, echo=False, user_settings=None, qt=False):
    """Creates and initialize a browser object"""
    if qt:
        implementation = QTWebKitMethods
    else:
        implementation = WebKitMethods

    browser = implementation.create_browser()
    implementation.set_settings(browser, user_settings)

    implementation.open_uri(browser, uri)

    def web_send(msg):
        if echo: print '<<<', msg
        asynchronous_gtk_message(implementation.inject_javascript)(browser,
                                                                   msg)

    return browser, web_send
