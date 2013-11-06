#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# <LICENSE=apachev2>
from django.core.mail import send_mail, EmailMultiAlternatives
from smtplib import SMTPConnectError
import socket,logging
logger = logging.getLogger('notmm.controllers.wsgi')
#import logging

__all__ = ['send_mail_wrapper', 'send_html_mail']

def send_mail_wrapper(recipients, from_addr=None, subject=None, message=None):  
    """Send a email message to a list of recipients"""
    try:
        send_mail(subject, message, from_addr, recipients)
        #logger.info('mail sent to %d recipients' % len(recipient_list))
    except (SMTPConnectError, socket.error) as e:
        # temporary problem connecting to the smtp server
        logger.debug('temporary problem sending mail: %r' % e)
        return True
    
    return False

def send_html_mail(recipients, from_addr, subject=None, message=None,
    mimetype='text/html'):
    email = EmailMultiAlternatives(subject, message, from_addr, recipients)
    email.attach_alternative(message, mimetype)
    email.send()
    
    return None
