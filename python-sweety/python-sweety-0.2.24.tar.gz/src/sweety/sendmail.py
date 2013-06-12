#!/usr/bin/env python2.6

import argparse
import email
import email.encoders
import getpass
import mimetypes
import os
import shlex
import smtplib
import socket
import sys
import uuid

import program

def handle_image(path, **args):
    basename = os.path.basename(path)

    path = os.path.expandvars(path)
    path = os.path.expanduser(path)

    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    fp = open(path, 'r')
    att = email.MIMEImage.MIMEImage(fp.read(), _subtype=subtype)
    fp.close()

    attid = str(uuid.uuid1())
    att.add_header('Content-ID', attid)
    att.add_header('Content-Disposition', 'inline', filename=basename)

    return ('<div class="image"><img src="cid:%s"/></div>' % attid, att)

def handle_link(url, text='', **args):
    if not text:
        text = url
    return '<a href="%s">%s</a>' % (url, text)

def handle_att(path, **args):
    basename = os.path.basename(path)
    
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)

    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        fp = open(path)
        att = email.MIMEText.MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == 'image':
        fp = open(path, 'r')
        att = email.MIMEImage.MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == 'audio':
        fp = open(path, 'r')
        att = email.MIMEAudio.MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(path, 'r')
        att = email.MIMEBase.MIMEBase(maintype, subtype)
        att.set_payload(fp.read())
        fp.close()
        # Encode the payload using Base64
        email.encoders.encode_base64(att)

    attid = str(uuid.uuid1())
    att.add_header('Content-ID', attid)
    att.add_header('Content-Disposition', 'attachment', filename=basename)

    return (attid, att)


def sendmail(src, subject, recipients, sender):
    atts = []
    elements = []
    for l in src.split('\n'):
        l = l.strip()
        if l[:2] == '{{' and l[-2:] == '}}':
            cmd = l[2:-2].strip()
            
            parts = shlex.split(cmd)
            cmd = parts[0]
            del parts[0]
            
            args = {}
            for p in parts:
                if '=' in p:
                    k, v = p.split('=', 1)
                    args[k] = v
                else:
                    args[p] = True
                

            if cmd == 'image':
                # image link
                src, att = handle_image(**args)
                elements.append(src)
                atts.append(att)
            elif cmd == 'link':
                # link text url
                src = handle_link(**args)
                elements.append(src)
            elif cmd == 'att':
                id, att = handle_att(**args)
                atts.append(att)
        else:
            elements.append(l)

            
    html = '''
<html>
    <head></head>
    <style>
    body, td, div {
        font-size: 100%%;
        line-height: 150%%;
    }
    </style>
    <body>
        <div>
%s
        </div>
    </body>
''' % '\n'.join(elements)
        
    msg = email.MIMEMultipart.MIMEMultipart('alternative')
    html_part = email.MIMEText.MIMEText(html, 'html')
    msg.attach(html_part)

    #text_part = email.MIMEText.MIMEText(src)
    #msg.attach(text_part)

    root = email.MIMEMultipart.MIMEMultipart()
    root['Subject'] = subject
    root['From'] = sender
    root['Reply-to'] = sender
    root['To'] = ', '.join(recipients)
    root.attach(msg)

    for att in atts:
        root.attach(att)

    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(sender, recipients, root.as_string())
    smtp.quit()



class SendmailProgram(program.Program):
    def __init__(self):
        super(SendmailProgram, self).__init__()

    def initialize(self):
        super(SendmailProgram, self).initialize()
        
        self.argparser.add_argument('-S', '--subject', dest = 'SUBJECT',
                                    action = 'store', default = '<no subject>',
                                    help = 'specify the email subject. [default: %(default)s]')
        self.argparser.add_argument('-s', '--sender', dest = 'SENDER',
                                    action = 'store', default = '%s@%s' % (getpass.getuser(), os.uname()[1]),
                                    help = 'specify the sender. [default: %(default)s')
        self.argparser.add_argument('-r', '--recipients', dest = 'RECIPIENTS',
                                    action = 'store', nargs = '+', required = True,
                                    help = 'specify the recipients.')

    def finalize(self):
        super(SendmailProgram, self).finalize()
        
    def run(self):
        content = sys.stdin.read()
        sendmail(content, self.prog_args.SUBJECT, self.prog_args.RECIPIENTS, 
                 self.prog_args.SENDER)

if __name__ == '__main__':
    program.main(SendmailProgram)
