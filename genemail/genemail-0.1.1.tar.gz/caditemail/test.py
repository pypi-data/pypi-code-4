# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2012/11/20
# copy: (C) Copyright 2012 Cadit Inc., All Rights Reserved.
#------------------------------------------------------------------------------

# todo: convert all MultiLineEqual()'s that compare XML to normalize
#       the XML first.

import sys, unittest, base64, difflib, re

from .manager import Manager, StringProvider
from .sender import Sender, StoredSender
from . import emailprov

def eqstrip(val):
  return val.replace('\n', '').replace('\r\n', '').replace(' ', '')

#------------------------------------------------------------------------------
class TestEmail(unittest.TestCase):

  maxDiff = None

  #----------------------------------------------------------------------------
  def test_inlineHtmlStyling(self):
    html = '<html><body><div>foo</div></body></html>'
    css  = 'body{color:red}body > div{font-size:10px}'
    chk  = '''<html xmlns="http://www.w3.org/1999/xhtml">
    <body style="color: red">
      <div style="font-size: 10px">foo</div>
    </body>
  </html>
'''
    xdoc = emailprov.parseXml(html)
    xdoc = emailprov.inlineHtmlStyling(xdoc, css)
    out  = emailprov.serializeHtml(xdoc)
    self.assertEqual(eqstrip(out), eqstrip(chk))

  #----------------------------------------------------------------------------
  def test_subject_element(self):
    tpl = '''<html
   xmlns="http://www.w3.org/1999/xhtml"
   xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
   >
   <head>
    <title><email:subject share="content">${message.title()}</email:subject></title>
   </head>
   <body>
    <p>${message}.</p>
   </body>
  </html>
'''
    chk = 'This Is A Test'
    eml = Manager(sender=StoredSender(), provider=StringProvider(tpl)).newEmail()
    eml['message'] = 'This is a test'
    self.assertEqual(eqstrip(chk), eqstrip(eml.getSubject()))
    # TODO: ensure share="content" works... (it doesn't currently...)

  #----------------------------------------------------------------------------
  def test_subject_entities(self):
    tpl = '''<html
   xmlns="http://www.w3.org/1999/xhtml"
   xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
   >
   <head>
    <title email:subject="content">${message.title()}&nbsp;&mdash;&nbsp;And More!...</title>
   </head>
   <body>
    <h1>Foo &amp; Bar</h1>
    <p>${message}&nbsp;&mdash;&nbsp;and more!...</p>
   </body>
  </html>
'''
    schk = 'This & That -- And More!...'
    hchk = '''<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
      <title>This &amp; That&#160;&#8212;&#160;And More!...</title>
    </head>
    <body>
    <h1>Foo &amp; Bar</h1>
    <p>This &amp; that&#160;&#8212;&#160;and more!...</p>
   </body>
  </html>
'''
    eml = Manager(sender=StoredSender(), provider=StringProvider(tpl)).newEmail()
    eml['message'] = 'This & that'
    self.assertEqual(schk, eml.getSubject())
    self.assertEqual(eqstrip(hchk), eqstrip(eml.getHtml()))

  #----------------------------------------------------------------------------
  def test_subject_attribute(self):
    tpl = '''<html
   xmlns="http://www.w3.org/1999/xhtml"
   xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
   >
   <head>
    <title email:subject="content">${message.title()}</title>
   </head>
   <body>
    <p>${message}.</p>
   </body>
  </html>
'''
    chk = 'This Is A Test'
    eml = Manager(sender=StoredSender(), provider=StringProvider(tpl)).newEmail()
    eml['message'] = 'This is a test'
    self.assertEqual(eqstrip(chk), eqstrip(eml.getSubject()))

  #----------------------------------------------------------------------------
  def test_subject_maxlength(self):
    tpl = '''<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
 >
 <head>
  <title><email:subject share="content">${message.title()}</email:subject></title>
 </head>
 <body>
  <p>${message}.</p>
 </body>
</html>
'''
    chk = 'This Is A Test [...]'
    man = Manager(sender=StoredSender(), provider=StringProvider(tpl))
    man.defaultMaxSubjectLength = 20
    eml = man.newEmail()
    eml['message'] = 'This is a test of capping the subject length'
    self.assertEqual(chk, eml.getSubject())
    chk2 = 'This [...]'
    eml2 = man.newEmail()
    eml2.maxSubjectLength = 10
    eml2['message'] = 'This is a test of capping the subject length'
    self.assertEqual(chk2, eml2.getSubject())

  #----------------------------------------------------------------------------
  def test_subject_snip(self):
    tpl = '''<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
 >
 <head>
  <title><email:subject share="content">${message.title()}</email:subject></title>
 </head>
 <body>
  <p>${message}.</p>
 </body>
</html>
'''
    chk = 'This Is [...snip...]'
    man = Manager(sender=StoredSender(), provider=StringProvider(tpl))
    man.defaultMaxSubjectLength = 20
    man.defaultSnipIndicator = '[...snip...]'
    eml = man.newEmail()
    eml['message'] = 'This is a test of changing the snip indicator'
    self.assertEqual(chk, eml.getSubject())

  #----------------------------------------------------------------------------
  def test_deprecationwarning_workaround(self):
    html = '<html><body><p class="f">first</p><p>second</p></body></html>'
    css  = 'p{background:#666;}p.f{background:#042d5a;}'
    import warnings
    warnings.filterwarnings(
      "error",
      message='Call to deprecated method \'_[sg]etCSSValue\'. Use ``property.propertyValue`` instead.',
      category=DeprecationWarning,
      module='cssutils.css.cssstyledeclaration',
      lineno=598,
      )
    xdoc = emailprov.parseXml(html)
    xdoc = emailprov.inlineHtmlStyling(xdoc, css)
    out  = emailprov.serializeHtml(xdoc)
    self.assertEqual(eqstrip('''<html xmlns="http://www.w3.org/1999/xhtml">
  <body>
    <p class="f" style="background: #042d5a">first</p>
    <p style="background: #666">second</p>
  </body>
</html>
'''),
                     eqstrip(out))

  #----------------------------------------------------------------------------
  def test_simpleEmail_textOnly(self):
    tpl = '''<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
 >
 <head>
  <email:header name="To">test@example.com</email:header>
  <email:header name="From" value="noreply@example.com">this-is-bogus</email:header>
  <email:env name="unused">feedback value</email:env>
  <title email:subject="content">${message.title()}</title>
 </head>
 <body>
  <p>${message}.</p>
  <p>Also sent to: <span email:header="CC">foo@example.com</span>.</p>
 </body>
</html>
'''
    tchk = '''This is a test.\n\nAlso sent to: foo@example.com.\n\n'''
    etchk = '''MIME-Version: 1.0
Content-Type: text/plain; charset="us-ascii"
Content-Transfer-Encoding: 7bit
From: noreply@example.com
CC: foo@example.com
To: test@example.com
Date: Fri, 13 Feb 2009 23:31:30 -0000
Message-ID: <1234567890@caditapp.email.test>
Subject: This Is A Test\n\n''' + tchk
    hchk = '''<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>This Is A Test</title>
  </head>
  <body>
  <p>This is a test.</p>
  <p>Also sent to: <span>foo@example.com</span>.</p>
 </body>
</html>
'''
    eml = Manager(sender=StoredSender(), provider=StringProvider(tpl)).newEmail()
    #eml.setHeader('From', 'noreply@example.com')
    #eml.setHeader('To', 'test@example.com')
    # override the UNpredictable generated info...
    eml.setHeader('Date', 'Fri, 13 Feb 2009 23:31:30 -0000')
    eml.setHeader('Message-ID', '<1234567890@caditapp.email.test>')
    eml.include = ['text']
    eml['message'] = 'This is a test'
    eml.send()
    self.assertEqual(1, len(eml.manager.sender.emails))
    out = eml.manager.sender.emails[0]
    self.assertEqual(eqstrip(etchk), eqstrip(out['message']))
    self.assertEqual(eqstrip(tchk), eqstrip(eml.getText()))
    self.assertEqual(eqstrip(hchk), eqstrip(eml.getHtml()))
    self.assertEqual(sorted(['test@example.com', 'foo@example.com']),
                     sorted(out['recipients']))

  #----------------------------------------------------------------------------
  def test_cidCleanup(self):
    tpl = '''<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
 >
 <head>
  <email:header name="To">test@example.com</email:header>
  <email:header name="From" value="noreply@example.com">this-is-bogus</email:header>
  <title email:subject="content">${message.title()}</title>
  <email:attachment name="smiley.png" encoding="base64" cid="true">
   dGhpcyBpcyBhIGJvZ3VzIGltYWdlCg==
  </email:attachment>
 </head>
 <body>
  <p>${message}.</p>
  <p>Also sent to: <span email:header="CC">foo@example.com</span>.</p>
  <p><img alt="smiley" src="cid:smiley.png"/></p>
 </body>
</html>
'''
    chk = '''This is a test.

Also sent to: foo@example.com.

[smiley]

'''
    eml = Manager(sender=StoredSender(), provider=StringProvider(tpl)).newEmail()
    eml['message'] = 'This is a test'
    self.assertEqual(eqstrip(chk), eqstrip(eml.getText()))

  #----------------------------------------------------------------------------
  def test_inlineStyling(self):
    tpl = '''<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
 >
 <head>
  <email:header name="To">test@example.com</email:header>
  <email:header name="From" value="noreply@example.com">this-is-bogus</email:header>
  <title email:subject="content">${message.title()}</title>
<style type="text/css">
p > span { font-weight: bold; }
  </style>
 </head>
 <body>
  <p>${message}.</p>
  <p>Also sent to: <span email:header="CC">foo@example.com</span>.</p>
 </body>
</html>
'''
    tchk = '''This is a test.\n\nAlso sent to: foo@example.com.\n\n'''
    etchk = '''MIME-Version: 1.0
Content-Type: text/plain; charset="us-ascii"
Content-Transfer-Encoding: 7bit
From: noreply@example.com
CC: foo@example.com
To: test@example.com
Date: Fri, 13 Feb 2009 23:31:30 -0000
Message-ID: <1234567890@caditapp.email.test>
Subject: This Is A Test\n\n''' + tchk
    hchk = '''<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>This Is A Test</title>
  </head>
  <body>
  <p>This is a test.</p>
  <p>Also sent to: <span style="font-weight: bold">foo@example.com</span>.</p>
 </body>
</html>
'''
    eml = Manager(sender=StoredSender(), provider=StringProvider(tpl)).newEmail()
    #eml.setHeader('From', 'noreply@example.com')
    #eml.setHeader('To', 'test@example.com')
    # override the UNpredictable generated info...
    eml.setHeader('Date', 'Fri, 13 Feb 2009 23:31:30 -0000')
    eml.setHeader('Message-ID', '<1234567890@caditapp.email.test>')
    eml.include = ['text']
    eml['message'] = 'This is a test'
    eml.send()
    #self.assertMultiLineEqual(etchk, eml.manager.sender.emails[0]['message'])
    #self.assertMultiLineEqual(tchk, eml.getText())
    self.assertEqual(eqstrip(hchk), eqstrip(eml.getHtml()))

  #----------------------------------------------------------------------------
  def test_email_rawSmtp(self):
    tpl = '''<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
 >
 <head>
  <email:header name="To">test@example.com</email:header>
  <email:header name="From" value="noreply@example.com"/>
  <email:attachment name="smiley.png" encoding="base64" cid="true">
   iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsTAAALEwEAmpwYAAAA
   IGNIUk0AAHolAACAgwAA+f8AAIDpAAB1MAAA6mAAADqYAAAXb5JfxUYAAAK0SURBVHjabJNfaJNX
   GMZ/X/IlaWub1NqWzLY6dYyiKAWxF0MdyC4KgjeObWy72G28EESam93sOlUZA82Nt2OMiWWwQmFg
   BXfVIQ6JqdY0sRi1TZfG/OmX7/vOOXm9KIRU+8KB9+F9zvPAe85jiQidtfrnxJCIJIAphEkBEFkU
   mEdIH774eKOTb3UKFO6emA6E+1LR0c/pHjxGV+wQAG61wNZGhurqAtqvJz/96snMBwK5O8dvxcbO
   Jvo//oJQpBdaLiJqm2SFINCFcuuU83+zWVhIH/3u6aW2wPLvx1KxsTPTw+MXQFdA/Y/oGrScbZtA
   D5YdhdAg2Ht5nZmlnL8/c+KH50kr++v4SDASKx757DKWWgPvFYv35kE0p05PAPDvP/+BZTN5bgoi
   I4gdJ7twDd+pjAa0NolYfALLySO1DNIosJJdZmUpD34T/CYrS3lWsstIo4DUMljNPAMjJ9HKJGyt
   zPk9PV20qllQFRDTXqr47o4XEq8BfhPxXfp6h1DKnLe1Nkcjpoy4b3ZcBhDl7o6VSyQEWptDtlKm
   qRtvwsHWVpv4zdXbAJjczV0xQEtvoJQJ2lqZQrNentgTbrWHeunGDuf3MYDjltDK5AJa6bnN8ltE
   +YjyWXz0st2/fzpnpVIFrcxcQCmTfrnewPguaI8DBw7y4GGRtfUqnuPgOQ5r61UePCwyFAuB9jC+
   y4vXVbQ2aUtE+Oun/tTIgD09vr8Lb+9ZNktFni0/p16vAdDXF+XIaIyP4kPYzQKZ1S1W192ZL1PN
   ZPsrz/7Ye2tsIJQ4vL+f7micQPQTLLt3e/u6QauWw6kUyb2q8qLkpb++7l36IEx/JLunw0FSB/fZ
   DEeD9PcEAKhsGUo1Q2FD4fqt5Lc/q5ld0wjw25VwXCCByJTAJNt5XhRhHkh//4te6+S/GwD2npI7
   ZK15EgAAAABJRU5ErkJggg==
  </email:attachment>
  <title email:subject="content">${message.title()}</title>
 </head>
 <body>
  <p>${message}.</p>
  <p><img alt="smiley" src="cid:smiley.png"/></p>
 </body>
</html>
'''
    schk = 'This And That'
    hchk = '''<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>This And That</title>
  </head>
  <body>
  <p>This and that.</p>
  <p><img alt="smiley" src="cid:smiley.png"/></p>
 </body>
</html>
'''

    regex = re.compile('.*<email:attachment[^>]*>([^<]*)</email:attachment>.*', re.DOTALL)

    chk = '''Content-Type: multipart/alternative; boundary="==caditapp.email.test=="
MIME-Version: 1.0
Date: Fri, 13 Feb 2009 23:31:30 -0000
To: test@example.com
Message-ID: <1234567890@caditapp.email.test>
From: noreply@example.com
Subject: This And That

--==caditapp.email.test==
MIME-Version: 1.0
Content-Type: text/plain; charset="us-ascii"
Content-Transfer-Encoding: 7bit

This and that.

[smiley]


--==caditapp.email.test==
Content-Type: multipart/related; boundary="==caditapp.email.test-related=="
MIME-Version: 1.0

--==caditapp.email.test-related==
MIME-Version: 1.0
Content-Type: text/html; charset="us-ascii"
Content-Transfer-Encoding: 7bit

<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>This And That</title>
  </head>
  <body>
  <p>This and that.</p>
  <p><img alt="smiley" src="cid:smiley.png"/></p>
 </body>
</html>

--==caditapp.email.test-related==
Content-Type: image/png; name="smiley.png"
MIME-Version: 1.0
Content-Transfer-Encoding: base64
Content-Disposition: attachment
Content-ID: <smiley.png>

''' + regex.sub('\\1', tpl).replace('   ','').strip() + '''
--==caditapp.email.test-related==--
--==caditapp.email.test==--'''


    eml = Manager(sender=StoredSender(), provider=StringProvider(tpl)).newEmail()
    # override the UNpredictable generated info...
    eml.setHeader('Date', 'Fri, 13 Feb 2009 23:31:30 -0000')
    eml.setHeader('Message-ID', '<1234567890@caditapp.email.test>')
    eml.boundary = 'caditapp.email.test'
    eml['message'] = 'This and that'
    eml.send()
    self.assertEqual(schk, eml.getSubject())
    self.assertEqual(eqstrip(hchk), eqstrip(eml.getHtml()))
    self.assertEqual(eqstrip(chk), eqstrip(eml.manager.sender.emails[0]['message']))

  #----------------------------------------------------------------------------
  def test_reduce2ascii_is_needed(self):
    from .emailprov import reduce2ascii as r2a
    self.assertRaises(UnicodeEncodeError,
                      u'this \u21d2 that'.encode,
                      'ascii')
    r2a(u'this \u21d2 that').encode('ascii')

  #----------------------------------------------------------------------------
  def test_reduce2ascii(self):
    from .emailprov import reduce2ascii as r2a
    self.assertEqual('this => that', r2a(u'this \u21d2 that'))
    self.assertEqual('this <- that', r2a(u'this \u2190 that'))
    self.assertEqual('this <= that', r2a(u'this \u21e6 that'))
    self.assertEqual(
      '->=>->=>=>->|->->|->=>>->|=>~>->>->',
      r2a(u'\u2192\u21d2\u21ac\u21c9\u21e8\u21e5\u21e2\u21aa\u21a6\u21f6\u21a3\u21f0\u219d\u21a0\u21fe'))

  #----------------------------------------------------------------------------
  def test_bccHeader(self):
    tpl = '''<html
 lang="en"
 xml:lang="en"
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
 >
 <head>
  <title email:subject="content">${message.title()}</title>
  <email:header name="to">rcpt@example.com</email:header>
  <email:header name="from">mailfrom@example.com</email:header>
 </head>
 <body><p>${message}.</p></body>
</html>
'''
    sender  = StoredSender()
    manager = Manager(sender=sender, provider=StringProvider(tpl))
    eml = manager.newEmail()
    eml['message'] = 'test'
    eml.setHeader('BcC', 'bcc@example.com')
    # override the UNpredictable generated info...
    eml.setHeader('date', 'Fri, 13 Feb 2009 23:31:30 -0000')
    eml.setHeader('message-id', '<1234567890@caditapp.email.test>')
    eml.boundary = 'caditapp.email.test'
    eml.send()
    self.assertEqual(1, len(sender.emails))
    out = sender.emails[0]
    self.assertEqual(sorted(['mailfrom', 'recipients', 'message']), sorted(out.keys()))
    self.assertEqual('mailfrom@example.com', out['mailfrom'])
    self.assertEqual(sorted(['rcpt@example.com', 'bcc@example.com']), sorted(out['recipients']))
    # ensure that the 'bcc' headers is stripped out of the output
    chk = '''Content-Type: multipart/alternative; boundary="==caditapp.email.test=="
MIME-Version: 1.0
From: mailfrom@example.com
To: rcpt@example.com
Date: Fri, 13 Feb 2009 23:31:30 -0000
Message-ID: <1234567890@caditapp.email.test>
Subject: Test

--==caditapp.email.test==
MIME-Version: 1.0
Content-Type: text/plain; charset="us-ascii"
Content-Transfer-Encoding: 7bit

test.


--==caditapp.email.test==
Content-Type: multipart/related; boundary="==caditapp.email.test-related=="
MIME-Version: 1.0

--==caditapp.email.test-related==
MIME-Version: 1.0
Content-Type: text/html; charset="us-ascii"
Content-Transfer-Encoding: 7bit

<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
  <head>
    <title>Test</title>
  </head>
  <body>
    <p>test.</p>
  </body>
</html>

--==caditapp.email.test-related==--
--==caditapp.email.test==--'''
    self.assertEqual(eqstrip(chk), eqstrip(out['message']))

  #----------------------------------------------------------------------------
  def test_managerBccHeader(self):
    tpl = '''<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
 >
 <head>
  <title email:subject="content">${message.title()}</title>
  <email:header name="to">rcpt@example.com</email:header>
  <email:header name="from">mailfrom@example.com</email:header>
 </head>
 <body><p>${message}.</p></body>
</html>
'''
    sender  = StoredSender()
    class MyManager(Manager):
      def updateHeaders(self, emailobj, headers):
        super(MyManager, self).updateHeaders(emailobj, headers)
        headers['bcc'] = 'bcc@example.com'
    manager = MyManager(sender=sender, provider=StringProvider(tpl))
    eml = manager.newEmail()
    eml['message'] = 'test'
    # override the UNpredictable generated info...
    eml.setHeader('date', 'Fri, 13 Feb 2009 23:31:30 -0000')
    eml.setHeader('message-id', '<1234567890@caditapp.email.test>')
    eml.send()
    self.assertEqual(1, len(sender.emails))
    out = sender.emails[0]
    self.assertEqual(sorted(['rcpt@example.com', 'bcc@example.com']), sorted(out['recipients']))

  # #----------------------------------------------------------------------------
  # def test_multiBccHeader(self):
  #   # todo
  #   pass

  #----------------------------------------------------------------------------
  def test_env_extraction(self):
    tpl = '''<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:email="http://xmlns.cadit.com/caditapp/email/1.0"
 >
 <head>
  <email:header name="To">test@example.com</email:header>
  <email:header name="From" value="noreply@example.com">this-is-bogus</email:header>
  <email:env name="env-name">feedback env-value</email:env>
  <title email:subject="content">${message.title()}</title>
 </head>
 <body>
  <p>${message}.</p>
  <p>Also sent to: <span email:header="CC">foo@example.com</span>.</p>
 </body>
</html>
'''

    eml = Manager(sender=StoredSender(), provider=StringProvider(tpl)).newEmail()
    self.assertEqual(eml.getEnv('env-name'), 'feedback env-value')
    self.assertEqual(eml.getEnvs(), dict([['env-name', 'feedback env-value']]))

#------------------------------------------------------------------------------
if __name__ == '__main__':
  unittest.main() # pragma: no cover

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
