import xmlrpclib
import datetime

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings

from .errors import UbivoxAPIError

class UbivoxEmailBackend(BaseEmailBackend):

    def __init__(self, *args, **kwargs):

        super(UbivoxEmailBackend, self).__init__(*args, **kwargs)

        attrs = (
            "UBIVOX_API_USERNAME",
            "UBIVOX_API_PASSWORD",
            "UBIVOX_API_URL",
        )

        for attr in attrs:
            if not hasattr(settings, attr):
                raise RuntimeError("Missing {} from settings".format(attr))

        api_url = "https://{}:{}@{}".format(
            settings.UBIVOX_API_USERNAME,
            settings.UBIVOX_API_PASSWORD,
            settings.UBIVOX_API_URL[8:],  # strip https://
        )

        self.server = xmlrpclib.ServerProxy(api_url)

        try:
            self.server.ubivox.ping()
        except xmlrpclib.ProtocolError:
            raise RuntimeError("Error authenticating with Ubivox")

    def _send(self, msg):

        for rcpt in msg.recipients():

            try:

                self.server.ubivox.send_email_rfc2822(
                    rcpt,
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "",
                    msg.message().as_string()
                )

            except xmlrpclib.Fault, e:

                if not self.fail_silently:

                    raise UbivoxAPIError(
                        e.faultCode,
                        e.faultString
                    )

            except xmlrpclib.ProtocolError:

                raise RuntimeError("Error authenticating with Ubivox")

        return True

    def send_messages(self, email_messages):

        sent = 0

        for msg in email_messages:
            if self._send(msg):
                sent += 1

        return sent
