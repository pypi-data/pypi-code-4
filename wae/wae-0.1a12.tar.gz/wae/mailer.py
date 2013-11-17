# -*- coding: utf-8 -*-
import smtplib, tempfile, glob, os
import mimetypes
import email
from email import encoders
from email.header import Header
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import wae.connect
from wae.config import config
try:
    from pymongo.objectid import ObjectId
except:
    from bson.objectid import ObjectId


class BaseQueue:
    "发邮件队列(基类)"
    def put(self, to_addrs, subject, cc=[], from_addr="", text="", html="", encoding="utf-8", attachments=[]):
        """放入队列"""
        if type(to_addrs) in (types.ListType, types.TupleType):
            to_addrs = ", ".join(to_addrs)

        # 设定root信息
        msg_root = MIMEMultipart()
        msg_root['Subject'] = Header(subject, encoding)
        msg_root['To'] = to_addrs
        if len(cc)>0: msg_root['Cc'] = ", ".join(cc)
        if from_addr!="": msg_root['From'] = from_addr
        msg_root.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msg_alt = MIMEMultipart('alternative')
        msg_root.attach(msg_alt)

        #设定纯文本信息
        if text!="":
            msg_text = MIMEText(text, 'plain', encoding)
            msg_alt.attach(msg_text)

        #设定HTML信息
        if html!="":
            msg_text = MIMEText(html, 'html', encoding)
            msg_alt.attach(msg_text)

        # 附件
        for i, (path, sio) in enumerate(attachments):
            v = sio.getvalue()
            ctype, enc = mimetypes.guess_type(path)
            if ctype==None or enc!=None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            if maintype=="text":
                a = MIMEText(v, _subtype=subtype)
            elif maintype=="image":
                a = MIMEImage(v, _subtype=subtype)
            elif maintype=="audio":
                a = MIMEAudio(v, _subtype=subtype)
            else:
                a = MIMEBase(maintype, subtype)
                a.set_payload(v)
                encoders.encode_base64(a)
            a.add_header("Content-Disposition", "attachment", filename=str(Header(path, encoding)))
            a.add_header('Content-ID', '<attachment-%d>' % (i+1))
            msg_root.attach(a)
        return self._save(from_addr, to_addr, msg_root.as_string())

    def _save(self, from_addr, to_addr, text):
        """保存邮件队列"""
        raise NotImplementedError


class DbQueue(BaseQueue):
    "发邮件队列"
    def _save(self, from_addr, to_addr, text):
        d = {
                "from": from_addr,
                "to": to_addr,
                "text": text,
                "state": "pending",
                "ctime": datetime.datetime.now(),
                "tries": 0,
        }
        mdb = wae.connect.connect_mongodb()
        i = mdb.mail_outbox.save(d)


class BaseSender(object):
    "发邮件基类"
    def __init__(self):
        self.FROM = config.get("mailer", "from")
        self.SMTP = config.get("mailer", "smtp")
        self.USER = config.get("mailer", "user")
        self.PASS = config.get("mailer", "password")

    def _do_send(self, text):
        """发送邮件"""
        m = email.message_from_string(text)
        if m["from"]==None: m["From"] = "MbaBot <%s>" % self.FROM
        to = [email.utils.parseaddr(x.strip())[1] for x in m['to'].split(",")]
        if m['cc']!=None:
            to += [x.strip() for x in m['cc'].split(",")]

        smtp = smtplib.SMTP()
        #smtp.set_debuglevel(1)
        smtp.connect(self.SMTP)
        #smtp.starttls()
        smtp.login(self.USER, self.PASS)
        smtp.sendmail(self.FROM, to, m.as_string())
        smtp.quit()

    def send(self, mailid):
        raise NotImplementedError

    @classmethod
    def scan(cls):
        raise NotImplementedError


class DbSender(BaseSender):
    def send(self, mailid):
        mdb = wae.connect.connect_mongodb()

        mi = ObjectId(mailid)
        m = mdb.mail_outbox.find_one({"_id":mi})
        if m!=None and m['state']=='pending':
            try:
                self._do_send(m['text'].encode("utf-8"))
                mdb.mail_outbox.update({"_id":mi}, {"$set":{"state":"done", "mtime":datetime.datetime.now()}, "$inc":{"tries":1}})
            except:
                mdb.mail_outbox.update({"_id":mi}, {"$inc":{"tries":1}, "$set":{"mtime":datetime.datetime.now()}})
                raise

