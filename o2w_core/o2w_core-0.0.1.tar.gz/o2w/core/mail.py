from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, EmailMessage

class Mail(object):
    
    def __init__(self, from_email=None, to=None, subject=None, context=None, bcc=[]):
        self.from_email = from_email
        self.to = to
        self.subject = subject
        self.context=context
        self.bcc = bcc
        
    def from_email(self, from_email):
        self.from_email = from_email
        return self

    def to(self, to):
        self.to = to
        return self

    def bcc(self, bcc):
        self.bcc = bcc
        return self

    def subject(self, subject):
        self.subject = subject
        return self

    def message(self, context, template_text="email/email.txt", template_html=None):
        self.context = context
        self.template_text = template_text
        self.template_html = template_html
        return self

    def has_text(self):
        return self.template_text

    def get_text(self):
        return render_to_string(self.template_text, self.context)
        
    def has_html(self):
        return self.template_html

    def get_html(self):
        return render_to_string(self.template_html, self.context)

    def is_multipart(self):
        return self.has_text() and self.has_html()
        
    def send(self):
        if self.is_multipart():
            msg = EmailMultiAlternatives(self.subject, self.get_text(), self.from_email, self.to, self.bcc)
            msg.attach_alternative(self.get_html(), "text/html")
        else:
            text = self.get_text() if self.has_text() else self.get_html()
            msg = EmailMessage(self.subject, text, self.from_email, self.to, self.bcc)
            if self.has_html():
                msg.content_subtype = "html"

        return msg.send()
