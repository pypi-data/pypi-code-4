from django.contrib import admin
from django.utils.text import truncate_words
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from emails.models import Recipient, Message

class RecipientInLine(admin.TabularInline):
    model = Recipient
        
class MessageAdmin(admin.ModelAdmin):
    inlines = [RecipientInLine]

    list_display = ('timestamp', 'subject', 'recipients', 'status')
    
    def recipients(self, obj):
        recipitents = Recipient.objects.filter(message = obj)
        
        return truncate_words(u', '.join([force_unicode(recipient) for recipient in recipitents]), 10)
    recipients.short_description = _('Recipients')
    
    def status(self, obj): 
        waiting_recipitents = Recipient.objects.filter(message = obj, sent = False)
        sent_recipitents = Recipient.objects.filter(message = obj, sent = True)
        
        if waiting_recipitents and sent_recipitents:
            background = '#FAE087'
            border = '#B0A16D'
            color ='#575755'
            status = _('Sending')
        elif sent_recipitents or (not waiting_recipitents and not sent_recipitents):
            background = '#C8DE96'
            border = '#94AC5E'
            color ='#585A56'
            status = _('Sent')
        else:
            background = '#BC3238'
            border = '#873034'
            color ='#FFFFFF'
            status = _('Waiting')
            
        return '<span style="display: block; text-align: center; width: 60px; padding: 1px 5px; background:%s;border-radius:3px;border:1px solid %s; color:%s;">%s</span>' % (background, border, color, force_unicode(status)) 
    status.short_description = _('State')
    status.allow_tags = True 

admin.site.register(Message, MessageAdmin)