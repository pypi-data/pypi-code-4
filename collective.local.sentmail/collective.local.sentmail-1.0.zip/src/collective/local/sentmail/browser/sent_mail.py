from plone import api
from plone.dexterity.browser.view import DefaultView
from email.utils import formataddr


class SentMailView(DefaultView):

    def update(self):
        super(SentMailView, self).update()
        creator = api.user.get(username=self.context.Creator())
        sender_fullname = creator.getProperty('fullname', None) or creator.getId()
        sender_email = creator.getProperty('email')
        if sender_email:
            self.mfrom = formataddr((sender_fullname, sender_email))
        else:
            self.mfrom = sender_fullname
        self.mto = []
        for username in self.context.recipients:
            _recipient = api.user.get(username=username)
            recipient_fullname = _recipient.getProperty('fullname', None) or \
                                _recipient.getId()
            recipient_email = _recipient.getProperty('email')
            if recipient_email:
                recipient = formataddr((recipient_fullname, recipient_email))
            else:
                recipient = recipient_fullname
            self.mto.append(recipient)
