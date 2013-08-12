
'''
Very simple and unicode friendly way to send email message from Python code.

Usage:

    sudo pip install send_email_message
    from send_email_message import send_email_message

    email_config = dict(
        host='smtp.gmail.com',
        port=587,
        tls=True, // Or ssl=True with another port.
        user='admin@example.com',
        password='password',
        from_name='Example Site',
        # Default: encoding='utf-8'
    )

    send_email_message(to='denisr@denisr.com', subject='Example News', text='Please see http://example.com/', **email_config)

send_email_message version 0.1.0
Copyright (C) 2013 by Denis Ryzhkov <denisr@denisr.com>
MIT License, see http://opensource.org/licenses/MIT
'''

#### import

from email.header import Header
from email.mime.text import MIMEText
import smtplib

#### send_email

def send_email_message(to, subject='', text='', encoding='utf-8', host='localhost', port=25, ssl=False, tls=False, user='admin@localhost', password='', from_name=''):

    SMTP = smtplib.SMTP_SSL if ssl else smtplib.SMTP
    smtp = SMTP(host, port)
    #smtp.set_debuglevel(True)
    if not ssl and tls:
        smtp.starttls()

    if password:
        smtp.login(user, password)

    if from_name:
        user = '{from_name} <{user}>'.format(from_name=from_name, user=user)

    msg = MIMEText(text.encode(encoding), 'plain', encoding)
    msg['From'] = user
    msg['To'] = to
    msg['Subject'] = Header(subject.encode(encoding), encoding)

    smtp.sendmail(user, to, msg.as_string())

    smtp.quit()
