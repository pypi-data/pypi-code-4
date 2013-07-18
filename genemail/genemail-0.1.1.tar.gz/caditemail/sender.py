# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2012/11/20
# copy: (C) Copyright 2012 Cadit Inc., All Rights Reserved.
#------------------------------------------------------------------------------

'''
The low-level mail sending agent. Used by the manager to delegate the
actual sending of the composed email. Note that the primary reason to
use a delegated object for this (rather than just using
smtplib.SMTP()) is so that an email can be serialized into another
form, such as for entry into a database or for unit testing and
comparison.
'''

#------------------------------------------------------------------------------
import smtplib
import email.parser

#------------------------------------------------------------------------------
class Sender(object):
  '''
  Abstract interface for an object capable of sending an
  ``caditapp.email``-generated email out, usually to an SMTP MTA.
  '''

  #----------------------------------------------------------------------------
  def send(self, mailfrom, recipients, message):
    '''
    Sends the specified `message` (in SMTP format) to the specified
    `recipients` coming from the email address `mailfrom`. Parameters:

    :param mailfrom:
      string, equivalent to the the SMTP ``MAIL FROM`` command.

    :param recipients:
      list of strings, equivalent to the SMTP ``RCPT TO`` command.

    :param message:
      the actuall message to be transferred, equivalent to the payload of
      the SMTP ``DATA`` command.
    '''
    raise NotImplementedError()

#------------------------------------------------------------------------------
class SmtpSender(Sender):
  '''
  An implementation of the :class:`caditapp.email.Sender` interface that
  connects to a local or remote SMTP server and submits the message for
  transfer or delivery. Constructor parameters:

  :param host:
    string, the SMTP server to connect to - defaults to the localhost.

  :param port:
    integer, the SMTP server port to connect to - defaults to 25, the
    standard SMTP port.

  :param ssl:
    indicates whether or not to connect using SSL.

  :param starttls:
    indicates that a STARTTLS command should be sent after connecting.

  :param username:
    [optional] set the SMTP username to authenticate as.

  :param password:
    [optional] set the password for the `username`.
  '''

  #----------------------------------------------------------------------------
  def __init__(self,
               host='localhost', port=25, ssl=False, starttls=False,
               username=None, password=None, *args, **kwargs):
    super(SmtpSender, self).__init__(*args, **kwargs)
    self.smtpHost = host or 'localhost'
    self.smtpPort = port or 25
    self.username = username
    self.password = password
    self.starttls = starttls
    self.ssl      = ssl

  #----------------------------------------------------------------------------
  def send(self, mailfrom, recipients, message):
    smtp = smtplib.SMTP_SSL() if self.ssl else smtplib.SMTP()
    smtp.connect(self.smtpHost, self.smtpPort)
    if self.starttls:
      smtp.starttls()
    if self.username is not None:
      smtp.login(self.username, self.password)
    smtp.sendmail(mailfrom, recipients, message)
    smtp.quit()

#------------------------------------------------------------------------------
class StoredSender(Sender):
  '''
  An implementation of the :class:`caditapp.email.Sender` interface
  that simply stores all messages in local memory in the
  :attr:`emails` attribute.  Most useful when unit testing email
  generation.
  '''

  #----------------------------------------------------------------------------
  def __init__(self, *args, **kwargs):
    super(StoredSender, self).__init__(*args, **kwargs)
    self.emails = []

  #----------------------------------------------------------------------------
  def send(self, mailfrom, recipients, message):
    self.emails.append(dict(mailfrom=mailfrom, recipients=recipients, message=message))

#------------------------------------------------------------------------------
class adict(dict):
  def __getattr__(self, key):
    return self.get(key, None)

#------------------------------------------------------------------------------
class DebugSender(StoredSender):
  '''
  An extension to the :class:`StoredSender` class that parses each
  email into it's MIME components, which simplifies unittesting. Each
  element in the `emails` attribute has the following attributes:

  * `mailfrom`:   SMTP-level `MAIL FROM` value (string)
  * `recipients`: SMTP-level `RCPT TO` value (list)
  * `message`:    raw SMTP `DATA` value (string)
  * `mime`:       the parsed :class:`email.message.Message` object
  * `from`:       email "From" header - not used by SMTP
  * `to`:         email "To" header - not used by SMTP
  * `date`:       email "Date" header
  * `subject`:    email "Subject" header
  * `plain`:      text/plain version of the email (or None)
  * `html`:       text/html version of the email (or None)
  * `calendar`:   text/calendar attachment of the email (or None)
  '''

  #----------------------------------------------------------------------------
  def send(self, mailfrom, recipients, message):
    eml = adict(mailfrom=mailfrom, recipients=recipients, message=message)
    mime = email.parser.Parser().parsestr(message)
    eml['mime']    = mime
    eml['from']    = mime.get('from')
    eml['to']      = mime.get('to')
    eml['date']    = mime.get('date')
    eml['subject'] = mime.get('subject')
    for part in mime.walk():
      ct = part.get_content_type()
      if not ct.startswith('text/'):
        continue
      ct = ct.split('/')[1]
      if eml.get(ct) is None:
        eml[ct] = part.get_payload()
      elif isinstance(eml[ct], list):
        eml[ct].append(part.get_payload())
      else:
        eml[ct] = [eml[ct], part.get_payload()]
    self.emails.append(eml)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
