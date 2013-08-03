# coding: utf-8
from django.template import defaultfilters
from django.utils.datastructures import SortedDict
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User
from django.db.models import Q
from django.utils.encoding import force_unicode
from django.core.urlresolvers import reverse
from django.db.utils import DatabaseError

from emails.engine import MailSender

def get_field_value(obj, field):
        val = getattr(obj, field.name)
        if field.choices: 
            val = obj._get_FIELD_display(field)
        if callable(val):
            val = val()
        
        if (field.get_internal_type() == "ManyToManyField"):
            val = u", ".join(m2mobj.__unicode__() for m2mobj in val.all())
        if (field.get_internal_type() == "DateTimeField"):
            return defaultfilters.date(val, settings.DATETIME_FORMAT)
        if (field.get_internal_type() == "DateField"):    
            return defaultfilters.date(val, settings.DATE_FORMAT)
        if (field.get_internal_type() ==  "BooleanField"):
            if (val): val = _('Yes')
            else: val = _('No')
        return val


class DefaultPostSave(object):
    
    def pre_register(self, model, **kwargs):
        pass
        
    def register(self, sender, **kwargs):
        self.pre_register(sender, **kwargs)
        post_save.connect(self.action, sender=sender)  

    def action(self, sender, instance, created, **kwargs):
        pass
    
class NotificationPostSave(DefaultPostSave):
    
    models_data = {}
    perm_name = 'can_receive_notification_%s'
    
    def pre_register(self, sender, **kwargs):
        try:
            subject = kwargs.get('subject', _('It was created a new item'))       
            template = kwargs.get('template','emails/notification.html')
            notification_fields = kwargs.get('notification_fields',[])
            
            
            self.models_data[sender._meta.db_table] = {
                                                      'subject': subject, 
                                                      'template': template, 
                                                      'notification_fields': notification_fields
                                                      }
    
            self.get_permission(sender)
        except DatabaseError:
            pass
            
    def get_permission(self, sender):
        content_type = ContentType.objects.get_for_model(sender)
        codename = self.perm_name % content_type.model
        permission, created = Permission.objects.get_or_create(content_type=content_type, codename=codename)
        return permission
                
    def recipients(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        codename = self.perm_name % content_type.model
        perm = self.get_permission(instance.__class__)
        
        users_qs = User.objects.filter(is_active=True, is_staff=True, email__isnull=False).exclude(email__exact='')
        if perm:
            users_qs = users_qs.filter(Q(groups__permissions=perm) | Q(user_permissions=perm) ).distinct()
        return users_qs.values_list('email', flat=True)
    
    def admin_url(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        object_admin_url = reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(instance.pk,))
        return object_admin_url
    
    def data(self, instance):
        data = SortedDict()
        
        for notification_field in self.models_data[instance._meta.db_table]['notification_fields'] :
            try:
                field = instance._meta.get_field(notification_field)
                data[field.verbose_name] =  get_field_value(instance, field)
            except AttributeError:
                pass
        
        return data
        
    def action(self, sender, instance, created, **kwargs):
        if (created):
            mail_sender = MailSender()
            context={'obj': instance,
                     'data': self.data(instance), 
                     'obj_verbose_name':instance._meta.verbose_name, 
                     'obj_name': instance._meta.object_name, 
                     'obj_app_label':instance._meta.app_label, 
                     'SITE_URL':settings.SITE_URL,
                     'object_admin_url': self.admin_url(instance)
                     }
             
            subject = force_unicode(self.models_data[instance._meta.db_table]['subject'])
            template = self.models_data[instance._meta.db_table]['template']  
            mail_sender.send_htmlmails(subject, self.recipients(instance), template, context)  

class FieldNotificationPostSave(DefaultPostSave):
    
    models_data = {}
    
    def register(self, sender, **kwargs):
        self.models_data[sender._meta.db_table] = {
                                                  'email_field': kwargs['email_field'], 
                                                  'subject': kwargs['subject'], 
                                                  'template': kwargs['template']
                                                  }
        super(FieldNotificationPostSave, self).register(sender, **kwargs)

        
    def action(self, sender, instance, created, **kwargs):
        if (created):
            mail_sender = MailSender()
            recip = getattr(instance, self.models_data[instance._meta.db_table]['email_field'])
            context={'obj': instance}
            mail_sender.send_htmlmail(self.models_data[instance._meta.db_table]['subject'], 
                                      recip, self.models_data[instance._meta.db_table]['template'], context)


send_notification = NotificationPostSave()
send_field_notification = FieldNotificationPostSave()
    