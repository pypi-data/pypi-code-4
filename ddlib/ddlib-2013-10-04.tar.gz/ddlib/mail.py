# -*- coding: utf-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.header import Header
from quopri import encodestring
from email.utils import formatdate
from email import encoders
import smtplib
import mimetypes
import os




class EMail(MIMEMultipart):
	"""
	from ddlib.mail import EMail

	EMail(
		from_email = 'from@email.com',
		to_email = 'to@email.com',
		subject = 'subject text',
		message = 'message text',
		reply_to = None,
		from_name = None,
		to_name = None,
		mtype = 'plain',
	).send(
		smtp_host = '',
		smtp_login = '',
		smtp_password = '',
		smtp_port = 465,
		ssl = 1,
	)
	"""

	def __init__(self, from_email, to_email, subject, message, reply_to=None, from_name=None, to_name=None, mtype='plain'):
		"""
			Klasa ułatwiająca wysyłanie wiadomości e-mail

			mtype
				'plain'		- wiadomość zwykłym tekstem
				'html'		- wiadomość HTML
		"""
		MIMEMultipart.__init__(self, 'related')
		assert isinstance(from_email, str), 'from_email - powinien byc <str>'
		assert isinstance(to_email, str), 'to_email - powinien byc <str>'
		assert isinstance(subject, str), 'subject - powinien byc <str>'
		assert isinstance(message, str), 'message - powinien byc <str>'
		assert mtype in ('plain', 'html'), 'mtype - powinien byc `plain` lub `html`'
		self.from_email = from_email
		self.to_email = to_email

		if from_name:
			assert isinstance(from_name, str), 'from_name - powinien byc <str>'
			tmp = Header(from_name, 'utf-8').encode()
			self['From'] = '"{}" <{}>'.format(tmp, from_email)

		else:
			self['From'] = from_email


		if to_name:
			assert isinstance(to_name, str), 'to_name - powinien byc <str>'
			tmp = Header(to_name, 'utf-8').encode()
			self['To'] = '"{}" <{}>'.format(tmp, to_email)

		else:
			self['To'] = to_email


		if reply_to:
			assert isinstance(reply_to, str), 'reply_to - powinien byc <str>'
			self['Reply-To'] = reply_to


		self['Subject'] = Header(subject, 'utf-8')
		self['Date'] = formatdate(localtime=1)

		msg = MIMEText(message, mtype, 'utf-8')
		self.attach(msg)


	def add_attach(self, filepath):
		ctype, encoding = mimetypes.guess_type(filepath)
		if ctype is None or encoding is not None: ctype = 'application/octet-stream'
		maintype, subtype = ctype.split('/', 1)
		fp = open(filepath, 'rb')
		msg = MIMEBase(maintype, subtype)
		msg.set_payload(fp.read())
		fp.close()
		encoders.encode_base64(msg)
		msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepath))
		self.attach(msg)


	def add_file_inline(self, filepath):
		ctype, encoding = mimetypes.guess_type(filepath)
		if ctype is None or encoding is not None: ctype = 'application/octet-stream'
		maintype, subtype = ctype.split('/', 1)
		fp = open(filepath, 'rb')
		msg = MIMEBase(maintype, subtype)
		msg.set_payload(fp.read())
		fp.close()
		encoders.encode_base64(msg)
		file_id = os.path.basename(filepath)
		msg.add_header('Content-ID', '<'+file_id+'>')
		msg.add_header('Content-Disposition', 'inline', filename=os.path.basename(filepath))
		self.attach(msg)
		return 'cid:%s'%file_id


	def save(self, filepath):
		p = open(filepath, 'wb')
		p.write(self.as_string())
		p.close()


	def send(self, smtp_host, smtp_port=465, smtp_login=None, smtp_password=None, ssl=1):
		if ssl: smtp = smtplib.SMTP_SSL(smtp_host, port=smtp_port)
		else: smtp = smtplib.SMTP(smtp_host, port=smtp_port)
		smtp.ehlo()
		if smtp_login and smtp_password: smtp.login(smtp_login, smtp_password)
		try:
			smtp.sendmail(self.from_email, self.to_email, self.as_string())

		except Exception as e:
			raise e

		finally:
			smtp.quit()


