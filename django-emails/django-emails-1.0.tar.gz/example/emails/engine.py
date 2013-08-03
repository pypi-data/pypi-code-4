from datetime import timedelta

from smtplib import SMTP

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

from django.template.loader import render_to_string
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils import timezone as datetime

from emails.models import Message, Recipient

class MailSender:
   
    def send_htmlmail(self, sbj, recip, template, context, priority=2, sender=None):
        text = render_to_string(template, context)
        self.send_mails(sbj, [recip], text, priority, 'html', sender)
        
    def send_htmlmails(self, sbj, recips, template, context, priority=2, sender=None):
        text = render_to_string(template, context)
        self.send_mails(sbj, recips, text, priority, 'html', sender)
        
    def send_mail(self, sbj, recip, text, priority=2, type='plain', sender=None):
        self.send_mails(sbj, [recip], text, priority, type, sender)
        
    def send_mails(self, sbj, recips, text, priority=2, type='plain', sender=None):
        if not recips:
            return
        
        if not sender:
            sender = settings.EMAIL_ADDRESS

        message = Message.objects.create(
            content = text,
            type = type,
            subject = force_unicode(sbj),
            sender_address = sender,
            priority = priority,
        )  
        
         
        for recip in recips:   
            Recipient.objects.create(
                address = recip,
                message = message
            )        
           
    def send(self, sbj, recip, content, sender, mimetype, charset='utf-8'):
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = sbj
        msgRoot['From'] = sender
        msgRoot['To'] =  recip
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
   
        msgAlternative.attach(MIMEText(content, mimetype, _charset=charset))
        
        self.smtp.sendmail(sender, recip, msgRoot.as_string())
    
    def connect(self):
        self.smtp = SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        
        if settings.EMAIL_USE_TLS:
            self.smtp.ehlo()
            self.smtp.starttls()
            self.smtp.ehlo() 
        if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD :
            self.smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    
    def quit(self):
        self.smtp.quit()
   
    
    def send_batch(self):
        num_send_mails = 0
        messages = Message.objects.filter(timestamp__lte = datetime.now(), 
                                          pk__in = Recipient.objects.filter(sent = False).values('message'))\
                                          .order_by('priority', '-timestamp') 
        out = []
        
        if (not messages.exists()):
            out.append("No mass emails to send.")
        else:
            batch = settings.COUNT_MAILS_IN_BATCH
            self.connect()       
            
            i = 0
            while num_send_mails < batch and messages.count() > i:
                message = messages[i]
                recipients = Recipient.objects.filter(message = message, sent = False)

                count_sent_mails = 0   
                for recipient in recipients:
                    self.send(message.subject, recipient.address, message.content, message.sender_address, message.type)
                    recipient.sent = True
                    recipient.save()
                    if num_send_mails == batch: break
                    num_send_mails += 1
                    count_sent_mails += 1
                
                out.append(u"Send {0} emails with date {1}.".format(count_sent_mails, message))    
        
                
            self.quit()
            
        self.delete_old_messages()
        return '\n'.join(out)  
    
    def delete_old_messages(self):
        Message.objects.filter(timestamp__lte = datetime.now() - timedelta(days=settings.COUNT_DAYS_TO_DELETE_MAIL))\
        .exclude(pk__in = Recipient.objects.filter(sent = False).values('message')).delete()
 
           
        
        
    