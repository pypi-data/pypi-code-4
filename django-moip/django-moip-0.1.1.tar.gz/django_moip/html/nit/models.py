#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
from django_moip.html.models import MoipHtmlBase
from django_moip.html.nit.signals import *


class MoipNIT(MoipHtmlBase):
    """Logs MoIP NIT interactions."""
    format = u"<NIT: %s %s>"

    class Meta:
        db_table = "moip_nit"
        verbose_name = "MoIP NIT"

    def send_signals(self):
        """Shout for the world to hear whether a txn was successful."""
        # Transaction signals:
        if self.is_transaction():
            if self.flag:
                payment_was_flagged.send(sender=self)
            else:
                payment_was_successful.send(sender=self)
        # Recurring payment signals:
        # XXX: Should these be merged with subscriptions?
        elif self.is_recurring():
            if self.is_recurring_create():
                recurring_create.send(sender=self)
            elif self.is_recurring_payment():
                recurring_payment.send(sender=self)
            elif self.is_recurring_cancel():
                recurring_cancel.send(sender=self)
            elif self.is_recurring_skipped():
                recurring_skipped.send(sender=self)
            elif self.is_recurring_failed():
                recurring_failed.send(sender=self)
       # Subscription signals:
        else:
            if self.is_subscription_cancellation():
                subscription_cancel.send(sender=self)
            elif self.is_subscription_signup():
                subscription_signup.send(sender=self)
            elif self.is_subscription_end_of_term():
                subscription_eot.send(sender=self)
            elif self.is_subscription_modified():
                subscription_modify.send(sender=self)            