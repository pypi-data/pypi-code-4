# -*- coding: utf-8 -*-
from Products.MailHost import MailHost
import email.Message

try:
    from Products.SecureMailHost.SecureMailHost import SecureMailHost
except ImportError:
    SecureMailHost = object

META_TYPE = 'MockMailHost'


class MockMailHost(MailHost.MailHost, SecureMailHost):

    meta_type = META_TYPE

    def __init__(self, id=''):
        super(MockMailHost, self).__init__(id)
        self.reset()

    def reset(self):
        self.messages = []
        self.msg_types = []
        self._p_changed = True

    def _send(self, mfrom, mto, messageText, debug=False):
        if isinstance(messageText, email.Message.Message):
            message = email.message_from_string(messageText)
        elif isinstance(messageText, email.message.Message):
            message = messageText.as_string()
        else:
            message = messageText
        self.messages.append(message)
        self._p_changed = True

    def send(self,
             messageText,
             mto=None,
             mfrom=None,
             subject=None,
             encode=None,
             immediate=False,
             charset=None,
             msg_type=None,
            ):
        self.msg_types.append(msg_type)
        super(MockMailHost, self).send(messageText, mto, mfrom,
             subject, encode, immediate, charset,
             msg_type)

    def pop(self, idx=-1):
        result = self.messages.pop(idx)
        self._p_changed = True
        return result

    def __len__(self):
        return len(self.messages)
