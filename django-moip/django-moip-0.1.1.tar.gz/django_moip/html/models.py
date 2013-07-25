#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django_moip.html.helpers import duplicate_txn_id, check_secret
from django_moip.html.conf import RECEIVER_EMAIL, POSTBACK_ENDPOINT, SANDBOX_POSTBACK_ENDPOINT

ST_MOIP_ACTIVE = 'Active'
ST_MOIP_CANCELLED = 'Cancelled'
ST_MOIP_CLEARED = 'Cleared'
ST_MOIP_COMPLETED = 'Completed'
ST_MOIP_DENIED = 'Denied'
ST_MOIP_PAID = 'Paid'
ST_MOIP_PENDING = 'Pending'
ST_MOIP_PROCESSED = 'Processed'
ST_MOIP_REFUSED = 'Refused'
ST_MOIP_REVERSED = 'Reversed'
ST_MOIP_REWARDED = 'Rewarded'
ST_MOIP_UNCLAIMED = 'Unclaimed'
ST_MOIP_UNCLEARED = 'Uncleared'

try:
    from idmapper.models import SharedMemoryModel as Model
except ImportError:
    Model = models.Model

class MoipHtmlBase(Model):
    """Meta class for common variables shared by NIT and PDT: http://tinyurl.com/cuq6sj"""
    # @@@ Might want to add all these one distant day.
    # FLAG_CODE_CHOICES = (
    # PAYMENT_STATUS_CHOICES = "Canceled_ Reversal Completed Denied Expired Failed Pending Processed Refunded Reversed Voided".split()
    PAYMENT_STATUS_CHOICES = (ST_MOIP_ACTIVE, ST_MOIP_CANCELLED, ST_MOIP_CLEARED, ST_MOIP_COMPLETED, ST_MOIP_DENIED, ST_MOIP_PAID, ST_MOIP_PENDING, ST_MOIP_PROCESSED, ST_MOIP_REFUSED, ST_MOIP_REVERSED, ST_MOIP_REWARDED, ST_MOIP_UNCLAIMED, ST_MOIP_UNCLEARED)
    # AUTH_STATUS_CHOICES = "Completed Pending Voided".split()
    # ADDRESS_STATUS_CHOICES = "confirmed unconfirmed".split()
    # PAYER_STATUS_CHOICES = "verified / unverified".split()
    # PAYMENT_TYPE_CHOICES =  "echeck / instant.split()
    # PENDING_REASON = "address authorization echeck intl multi-currency unilateral upgrade verify other".split()
    # REASON_CODE = "chargeback guarantee buyer_complaint refund other".split()
    # TRANSACTION_ENTITY_CHOICES = "auth reauth order payment".split()
    
    # Transaction and Notification-Related Variables
    test_nit = models.BooleanField(default=False, blank=True)
    txn_id = models.CharField("Transaction ID", max_length=19, blank=True, help_text="MoIP transaction ID.", db_index=True)

    # Buyer Information Variables
    payer_email = models.CharField(max_length=127, blank=True)

    # Payment Information Variables
    auth_amount = models.DecimalField(max_digits=64, decimal_places=2, default=0, blank=True, null=True)
    auth_status = models.CharField(max_length=9, blank=True) 
    payment_status = models.CharField(max_length=9, blank=True)
    payment_type = models.CharField(max_length=7, blank=True)

    # Variables not categorized
    receipt_id= models.CharField(max_length=64, blank=True)  # 1335-7816-2936-1451     
    handling_amount = models.DecimalField(max_digits=64, decimal_places=2, default=0, blank=True, null=True)
    transaction_subject = models.CharField(max_length=255, blank=True)

    # Non-MoIP Variables - full NIT/PDT query and time fields.    
    ipaddress = models.IPAddressField(blank=True)
    flag = models.BooleanField(default=False, blank=True)
    flag_code = models.CharField(max_length=16, blank=True)
    flag_info = models.TextField(blank=True)
    query = models.TextField(blank=True)  # What we sent to MoIP.
    response = models.TextField(blank=True)  # What we got back.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Where did it come from?
    from_view = models.CharField(max_length=6, null=True, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        if self.is_transaction():
            return self.format % ("Transaction", self.txn_id)
        else:
            return self.format % ("Recurring", self.recurring_payment_id)
        
    def is_transaction(self):
        return len(self.txn_id) > 0

    def is_recurring(self):
        return len(self.recurring_payment_id) > 0
    
    def is_subscription_cancellation(self):
        return self.txn_type == "subscr_cancel"
    
    def is_subscription_end_of_term(self):
        return self.txn_type == "subscr_eot"
    
    def is_subscription_modified(self):
        return self.txn_type == "subscr_modify"
    
    def is_subscription_signup(self):
        return self.txn_type == "subscr_signup"

    def is_recurring_create(self):
        return self.txn_type == "recurring_payment_profile_created"

    def is_recurring_payment(self):
        return self.txn_type == "recurring_payment"
    
    def is_recurring_cancel(self):
        return self.txn_type == "recurring_payment_profile_cancel"
    
    def is_recurring_skipped(self):
        return self.txn_type == "recurring_payment_skipped"
    
    def is_recurring_failed(self):
        return self.txn_type == "recurring_payment_failed"
    
    def set_flag(self, info, code=None):
        """Sets a flag on the transaction and also sets a reason."""
        self.flag = True
        self.flag_info += info
        if code is not None:
            self.flag_code = code
        
    def verify(self, item_check_callable=None):
        """
        Verifies an NIT and a PDT.
        Checks for obvious signs of weirdness in the payment and flags appropriately.
        
        Provide a callable that takes an instance of this class as a parameter and returns
        a tuple (False, None) if the item is valid. Should return (True, "reason") if the
        item isn't valid. Strange but backward compatible :) This function should check 
        that `mc_gross`, `mc_currency` `item_name` and `item_number` are all correct.

        """
        self.response = self._postback()
        self._verify_postback()  
        if not self.flag:
            if self.is_transaction():
                if self.payment_status not in self.PAYMENT_STATUS_CHOICES:
                    self.set_flag("Invalid payment_status. (%s)" % self.payment_status)
                if duplicate_txn_id(self):
                    self.set_flag("Duplicate txn_id. (%s)" % self.txn_id)
                if self.receiver_email != RECEIVER_EMAIL:
                    self.set_flag("Invalid receiver_email. (%s)" % self.receiver_email)
                if callable(item_check_callable):
                    flag, reason = item_check_callable(self)
                    if flag:
                        self.set_flag(reason)
            else:
                # @@@ Run a different series of checks on recurring payments.
                pass
        
        self.save()
        self.send_signals()

    def verify_secret(self, form_instance, secret):
        """Verifies an NIT payment over SSL using EWP."""
        if not check_secret(form_instance, secret):
            self.set_flag("Invalid secret. (%s)") % secret
        self.save()
        self.send_signals()

    def get_endpoint(self):
        """Set Sandbox endpoint if the test variable is present."""
        if self.test_nit:
            return SANDBOX_POSTBACK_ENDPOINT
        else:
            return POSTBACK_ENDPOINT

    def send_signals(self):
        """Shout for the world to hear whether a txn was successful."""

        # Don't do anything if we're not notifying!
        if self.from_view != 'notify':
            return

        # Transaction signals:
        if self.is_transaction():
            if self.flag:
                payment_was_flagged.send(sender=self)
            else:
                payment_was_successful.send(sender=self)
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


    def initialize(self, request):
        """Store the data we'll need to make the postback from the request object."""
        self.query = getattr(request, request.method).urlencode()
        self.ipaddress = request.META.get('REMOTE_ADDR', '')

    def _postback(self):
        """Perform postback to MoIP and store the response in self.response."""
        raise NotImplementedError
        
    def _verify_postback(self):
        """Check self.response is valid andcall self.set_flag if there is an error."""
        raise NotImplementedError
