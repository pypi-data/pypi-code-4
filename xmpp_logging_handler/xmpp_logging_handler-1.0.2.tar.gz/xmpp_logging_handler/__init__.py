import logging
from emitter import Send

VERSION = '1.0.1'
AUTHOR = 'Raymond McGinlay'
EMAIL = "raymond@thisislevelup.com"
URL = 'htpp://www.thisislevelup.com/'


class XMPPHandler(logging.Handler):
    """
    XMPPHandler for Python logging
    ------------------------------

    Usage example, assumes gmail.com account.

    ::

        from xmpp_logging_handler import XMPPHandler
        import logging
        logger = logging.getLogger()
        myHandler = XMPPHandler('SENDING_USER', 'SENDING_PASSWORD', ['raymond@thisislevelup.com',],)
        logger.addHandler(myHandler)
        logging.error('Its broken')

    """

    def __init__(self,
                 username=False,
                 password=False,
                 recipients=[],
                 host='gmail.com',
                 server='talk.google.com',
                 port=5223,
                 name='botty'):
        self.config_dict = {'username': username,
                            'password': password,
                            'host': host,
                            'server': server,
                            'port': port,
                            'name': name
                            }
        self.recipients = recipients
        logging.Handler.__init__(self)

    def emit(self, record):
        message = self.format(record)
        for recipient in self.recipients:
            Send(recipient, message, self.config_dict)
