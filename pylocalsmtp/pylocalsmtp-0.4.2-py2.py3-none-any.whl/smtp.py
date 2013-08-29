from datetime import datetime
from smtpd import SMTPServer
from email.Header import decode_header
from email import message_from_string
from .models import Mail


def get_first_text_part(msg):
    maintype = msg.get_content_maintype()
    if maintype == 'multipart':
        for part in msg.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return msg.get_payload()


def get_message_from_string(data):
    """
    Split the data receiced in process_message to :
    headers / subject / body

    Return a tuple.
    """
    msg = message_from_string(data)
    subject = msg['Subject']
    body = get_first_text_part(msg)
    headers = msg._headers
    string_headers = "\n".join([": ".join(header) for header in headers])
    return (
        string_headers, subject, body
    )


class ProxyDebugServer(SMTPServer):
    def __init__(self, localaddr, queue):
        self._localaddr = localaddr
        self._queue = queue
        SMTPServer.__init__(self, localaddr, ())

    def process_message(self, peer, mailfrom, rcpttos, data):
        headers, subject, body = get_message_from_string(data)
        mail = Mail(
            mail_from=mailfrom,
            mail_to=";".join(rcpttos),
            subject=decode_header(subject)[0][0],
            sent_date=datetime.now(),
            headers=headers,
            body=decode_header(body)[0][0]
        )
        mail.save()
        self._queue.put(mail)
