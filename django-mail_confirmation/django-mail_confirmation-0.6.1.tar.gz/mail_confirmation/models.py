from __future__ import absolute_import, unicode_literals

import random
import string

from django.db import models
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

import logging
logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class MailConfirmation(models.Model):
    """
    Handles a confirmation token randomly generated
    """
    confirmationid = models.CharField(verbose_name=_("Confirmation id"), 
                                      max_length=255, 
                                      unique=True)
    confirmed = models.BooleanField(verbose_name=_("Confirmed"),
                                    default=False)
    date_created = models.DateTimeField(verbose_name=_("Date created"),
                                    auto_now_add=True)
    confirm_success_template = models.CharField(verbose_name=_("Template that shows the user a success message on confirmation"),
                                                max_length=200,
                                                blank=True)
    confirm_success_url = models.CharField(verbose_name=_("Redirect the user to this url when the url is confirmed"),
                                           max_length=200,
                                           blank=True)
    toconfirm_type = models.ForeignKey(ContentType)
    toconfirm_id = models.PositiveIntegerField()
    toconfirm_object = generic.GenericForeignKey('toconfirm_type', 'toconfirm_id')

    def save(self, *args, **kwargs):
        if self.pk is not None:
            #updating existing model
            return super(MailConfirmation, self).save(*args, **kwargs)

        #this is pretty slow to generate!
        length = 50
        retry = 1024
        while retry>0:
            retry -= 1
            self.confirmationid = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(length))
            try:
                return super(MailConfirmation, self).save(*args, **kwargs)
            except IntegrityError, e:
                if e[1].find("confirmationid") == -1:
                    raise
        logger.error("Unable to generate mail_confirmation unique id, you could have won the lottery!")
        raise IntegrityError("mail_confirmation save error")

    def __str__(self):
        return self.confirmed
