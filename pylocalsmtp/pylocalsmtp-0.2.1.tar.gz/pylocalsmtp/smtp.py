from datetime import datetime
from smtpd import SMTPServer
from .models import Mail


def split_data(data):
    """
    Split the data receiced in process_message to :
    headers / subject / body

    Return a tuple.
    """
    lines = data.split('\n')
    headers = []
    subject = ""
    body = []
    inheaders = True
    for line in lines:
        # headers first
        if not line:
            inheaders = False
        if inheaders:
            if line.startswith("Subject: "):
                subject = line.replace("Subject: ", "")
            headers.append(line)
        else:
            body.append(line)
    return ("\n".join(headers), subject, "\n".join(body))


class ProxyDebugServer(SMTPServer):
    def __init__(self, localaddr, remoteaddr, queue):
        self._localaddr = localaddr
        self._remoteaddr = remoteaddr
        self._queue = queue
        SMTPServer.__init__(self, localaddr, remoteaddr)

    def process_message(self, peer, mailfrom, rcpttos, data):
        headers, subject, body = split_data(data)
        mail = Mail(
            mail_from=mailfrom,
            mail_to=";".join(rcpttos),
            subject=subject,
            sent_date=datetime.now(),
            headers=headers,
            body=body

        )
        mail.save()
        self._queue.put(mail)
