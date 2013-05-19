# coding=utf-8
import unittest
import os
import smtplib
import mimetypes

from email import encoders
from email.MIMEMultipart import MIMEMultipart
from email.Utils import formatdate
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.header import Header


__version__ ="0.0.2"

#my exceptions
class Error(Exception):
    """Base class for exceptions in this module."""
    pass
    def __str__(self):
        return repr(self.message)

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self,message):
        self.message = message

class TransitionError(Error):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, previous, next, message):
        self.previous = previous
        self.next = next
        self.message = message


class MailSender:
    """ MailSender user to send mail"""

    def __is_contains_nonascii_characters(self,str):
        """ check if the body contain nonascii charectoers"""
        return not all(ord(c) < 128 for c in str)   

    def __addheader(self,headername, headervalue):
        """ judge the message's charset and set header with "utf-8" when there is nonascii chracters """
        if self.__is_contains_nonascii_characters(headervalue):
            h = Header(headervalue, 'utf-8')
            self.msg[headername] = h
        else:
            self.msg[headername] = headervalue    


    def __init__(self,smtp_host=None,smtp_user=None,smtp_password=None):
        """
        Initial with smtp_user and password

        """
        self.msg = MIMEMultipart()
        self.smtp_host=smtp_host
        self.smtp_user=smtp_user
        self.smtp_password=smtp_password

    def add_subject(self,subject):
        """ add mail subject """
        self.__addheader('Subject',subject)

    def set_sender(self,sender):
        """ set mail sender """
        self.msg['from']=sender

    def set_to(self,recipients=[]):
        """ set mail recicipents,the parameter should be a list """
        COMMASPACE = ', '
        self.msg['to']=COMMASPACE.join(recipients)

    def add_text_body(self,body):
        """ add mail text body """
        if(self.__is_contains_nonascii_characters(body)):
            plaintext = MIMEText(body.decode("utf-8").encode('utf-8'),'plain','utf-8') 
        else:
            plaintext = MIMEText(body,'plain')
        self.msg.attach(plaintext)

    def add_html_body(self,body):
        """ add mail html body """
        if(self.__is_contains_nonascii_characters(body)):
            plaintext = MIMEText(body.decode("utf-8").encode('utf-8'),'html','utf-8') 
        else:
            plaintext = MIMEText(body,'html')
        self.msg.attach(plaintext)


    def add_attach(self,filePath):
        """ add mail attachment file"""
        if os.path.isfile(filePath):
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
            ctype, encoding = mimetypes.guess_type(filePath)
            if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)

            #add the attachment by guessed type

            if maintype == 'text':
                fp = open(filePath)
                # Note: we should handle calculating the charset
                filecontent = MIMEText(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'image':
                fp = open(filePath, 'rb')
                filecontent = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
            elif maintype == 'audio':
                fp = open(filePath, 'rb')
                filecontent = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
            else:
                fp = open(filePath, 'rb')
                filecontent = MIMEBase(maintype, subtype)
                filecontent.set_payload(fp.read())
                fp.close()
                # Encode the payload using Base64
                encoders.encode_base64(filecontent)

               # Set the filename parameter
            filecontent.add_header('Content-Disposition', 'attachment', filename=filePath)
            self.msg.attach(filecontent)
        else:
            raise Exception("the attached file is not existed")
    
    def send_mail(self,mail_from,mail_to):
        """ send mail """
        self.msg["From"] = mail_from
        self.msg["To"] = mail_to
        self.msg['Date']    = formatdate(localtime=True)

        #login to smtp server
        if self.smtp_user is None:
            raise Exception("no smpt user provided ")
        if self.smtp_host is  None:
            raise Exception("no smpt password provider")
        server = smtplib.SMTP(self.smtp_host)
        server.login(self.smtp_user,self.smtp_password)  # optional

        try:
            server.sendmail(self.msg['from'], self.msg['to'], self.msg.as_string())
            server.close()
        except Exception, e:
            errorMsg = "Unable to send email. Error: %s" % str(e)
            print errorMsg




