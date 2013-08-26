# -*- coding: utf8 -*-
import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

__author__ = 'ir4y'

class SMSReport(models.Model):
    """
    Отчет о отправке смс
    """
    SEND_RESPONCE_TYPE=(
        ('send',_(u'Статус сообщения не получен')),
        ('error',_(u'В ходе отправки произошла ошибка')),
        ('not_deliver',_(u'Cообщение не было доставлено')),
        ('expired',_(u'Абонент находился не в сети.')),
        ('deliver',_(u'Cообщение доставлено')),
        ('partly_deliver',_(u'Cообщение было отправлено, но статус так и не был получен.')),
    )
    created = models.DateTimeField(u'Дата создания',auto_now_add=True,default=datetime.datetime.now())
    sms_id = models.PositiveIntegerField(u'Идентификатор СМС',blank=True,null=True)
    response_status = models.CharField(u'Статус отправки',max_length=150,default='send',choices=SEND_RESPONCE_TYPE)
    mobile_phone = models.CharField(_(u'Номер телефона'),max_length=15,blank=True,null=True)
    text = models.CharField(u'Текст сообщения',max_length=200)
    error = models.TextField(verbose_name=_(u'Текст ошибки'),blank=True,null=True)

    def __unicode__(self):
        if self.response_status =='error':
            return u"{0}->{1}".format(self.mobile_phone,self.error)
        return u"{0}->{1}".format(self.mobile_phone,self.get_response_status_display())

    class Meta:
        verbose_name = _(u"Отчет о досавке")
        verbose_name_plural = _(u"Отчеты о доставке")



class SMSTemplate(models.Model):
    """
    Шаблон CМС сообщения
    """
    name = models.CharField(_(u'Название шаблона'),max_length=50)
    text = models.TextField(_(u'Шаблон'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"Шаблон СМС")
        verbose_name_plural = _(u"Шаблоны СМС")



