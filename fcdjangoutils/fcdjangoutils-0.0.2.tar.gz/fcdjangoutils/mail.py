# -*- coding: utf-8 -*-
import smtplib
import email.mime.text
import settings
import os.path

def send_template(template, info):
    """Send an email based on a template and a dictionary of data.

    Template is a dictionary of mail headers (key is header name,
    value is header value). The values are python format strings, and
    will be formatted with the info dictionary:

    mail_header[key] = template[key] % info
    
    The special "header" named "Body" is used to supply the body
    content of the message.
    """

    msg = email.mime.text.MIMEText(template['Body'] % info)
    for name, value in template.iteritems():
        if name != "Body":
            msg[name] = value % info

    if settings.MAILSERVER is None:
        f = open(os.path.join(os.path.dirname(__file__), "../mail.txt"), "a")
        f.write(msg.as_string())
        f.write("\n\n")
        f.close()
    else:
        s = smtplib.SMTP(*settings.MAILSERVER)
        s.connect()
        s.sendmail(msg["From"], msg["To"], msg.as_string())
        s.quit()
