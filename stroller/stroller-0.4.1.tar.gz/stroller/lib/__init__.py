# -*- coding: utf-8 -*-
import pylons, tg
from tg.i18n import get_lang
import tw.api
import tw.jquery
from smtplib import SMTP
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr

class IconLink(tw.api.Link):
    """
    A link to an icon.
    """
    template = """<img src="$link" alt="$alt" title="$title"/>"""
    
    params = dict(alt="Alternative text when not displaying image",
                  title="the tooltip of the image")
    
    def __init__(self, *args, **kw):
        super(IconLink, self).__init__(*args, **kw)
        self.alt = kw.get('alt')
        self.title = kw.get('alt')
        
manage_css = tw.api.CSSLink(modname = 'stroller', filename = 'static/manage.css')
style_css = tw.api.CSSLink(modname = 'stroller', filename = 'static/style.css')
confirm_css = tw.api.CSSLink(modname = 'stroller', filename = 'static/confirm.css')

def language():
    langs = []
    
    lang = get_lang()
    if lang:
        if isinstance(lang, list):
            langs.extend(lang)
        else:
            langs.append(lang)
        
    for lang in tg.request.languages:
        try:
            ltype, lsubtype = lang.split('-', 1)
        except:
            ltype, lsubtype = lang, lang
        
        if ltype != lsubtype:
            langs.append(lang)
        langs.append(ltype)
        
    langs.append(tg.config.get('default_language', 'en'))
    return langs

def stroller_url(path, *args, **kwargs):
    stroller_root = tg.config.get('stroller_root', '/shop')
    if path[0] == '/':
        path = stroller_root + path
    path = pylons.url(path, *args, **kwargs)
    return path

def send_email(sender, recipient, subject, body):
    header_charset = 'ISO-8859-1'
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            body.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break

    sender_name, sender_addr = parseaddr(sender)
    recipient_name, recipient_addr = parseaddr(recipient)

    sender_name = str(Header(unicode(sender_name), header_charset))
    recipient_name = str(Header(unicode(recipient_name), header_charset))

    sender_addr = sender_addr.encode('ascii')
    recipient_addr = recipient_addr.encode('ascii')

    msg = MIMEText(body.encode(body_charset), 'plain', body_charset)
    msg['From'] = formataddr((sender_name, sender_addr))
    msg['To'] = formataddr((recipient_name, recipient_addr))
    msg['Subject'] = Header(unicode(subject), header_charset)

    smtp = SMTP(tg.config.get('stroller_smtp_host', 'localhost'))
    if tg.config.get('stroller_smtp_login'):
        try:
            smtp.starttls()
        except:
            pass
        smtp.login(tg.config.get('stroller_smtp_login'),
                   tg.config.get('stroller_smtp_passwd'))
    smtp.sendmail(sender, recipient, msg.as_string())
    smtp.quit()
