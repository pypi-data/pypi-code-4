# coding: utf8

import logging

from django.conf import settings
from django.db import models

from django_extensions.db.models import TimeStampedModel

log = logging.getLogger('accountant.models')


class Account(TimeStampedModel):
    """
    Represents an account that contains funds that may be transfered to other
    accounts.
    """

    comment = models.CharField(max_length=200, blank=True)
    currency = models.CharField(max_length=6, default='USD')
    is_primary_destination = models.BooleanField(default=True)
    is_primary_source = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='accounts')

    class InsufficientBalance(Exception):
        def __init__(self, balance, amount):
            self.balance = balance
            self.amount = amount

        def __str__(self):
            return str('%0.2f < %0.2f' % (self.balance, self.amount))

        def __unicode__(self):
            return '%0.2f < %0.2f' % (self.balance, self.amount)

    def __unicode__(self):
        if self.comment:
            return unicode('[%s]%s (%s)' % (
                self.currency, self.user, self.comment))
        return '[%s]%s' % (self.currency, self.user)

    @classmethod
    def GetMasterAccount(cls, currency='USD'):
        """ Returns the site master account. """

        return cls.objects.get(
            pk=settings.MASTER_ACCOUNT_PK, currency=currency)

    @classmethod
    def GetPrimaryDestinationAccount(cls, user, currency='USD'):
        """ Returns the given user's primary destination account. """

        try:
            return cls.objects.get(
                user=user, is_primary_destination=True, currency=currency
            )
        except cls.DoesNotExist:
            log.error(
                'Primary destination account for user: %s does not exist.'
                % user
            )

    @classmethod
    def GetPrimarySourceAccount(cls, user, currency='USD'):
        """ Returns the given user's primary source account. """

        try:
            return cls.objects.get(
                user=user, is_primary_source=True, currency=currency
            )
        except cls.DoesNotExist:
            log.error(
                'Primary source account for user: %s does not exist.'
                % user
            )

    def get_deposits(self, only_settled=True):
        """ Returns the deposit transactions. """

        return self.destination_transactions.filter(
            amount__gt=0, is_settled=only_settled)
    deposits = property(get_deposits)

    def get_withdrawals(self, only_settled=True):
        """ Returns the withdrawal transactions. """

        return self.source_transactions.filter(
            amount__lt=0, is_settled=only_settled)
    withdrawals = property(get_withdrawals)

    def get_refreshed_balance(self, only_settled=True):
        """
        Sums the source transactions less than zero and the destination
        transactions greater than zero.
        """

        negatives = sum(map(
            lambda t: t.amount,
            self.get_withdrawals(only_settled=only_settled)
        ))

        positives = sum(map(
            lambda t: t.amount,
            self.get_deposits(only_settled=only_settled)
        ))

        return float(positives + negatives)
    refreshed_balance = property(get_refreshed_balance)

    def get_balance(self, only_settled=True):
        """
        Sums the source transactions less than zero and the destination
        transactions greater than zero.
        """
        return self.get_refreshed_balance(only_settled=only_settled)
    balance = property(get_balance)

    def transfer(self, amount, account, comment=''):
        """
        Transfers the amount from this account to the given account if the
        account has enough funds.
        """
        if self.balance < amount:
            log.error(
                'Account %d does not have enough funds to cover the transfer. '
                'Balance: %0.2f, Amount Requested: %0.2f, Comment: %s' % (
                    self.pk, self.balance, amount, comment
                )
            )

            raise self.__class__.InsufficientBalance(self.balance, amount)

        Transaction.objects.create(
            amount=amount * -1,
            is_settled=True,
            source_account=self,
            destination_account=account,
            comment=comment,
        )

        return Transaction.objects.create(
            amount=amount,
            is_settled=True,
            source_account=self,
            destination_account=account,
            comment=comment,
        )


class Transaction(TimeStampedModel):
    """ Represents a transfer of funds between two accounts. """

    amount = models.DecimalField(decimal_places=8, max_digits=24)
    comment = models.CharField(max_length=200, blank=True, default='')
    is_settled = models.BooleanField(default=False)

    source_account = models.ForeignKey(
        'accountant.Account',
        related_name='source_transactions'
    )

    destination_account = models.ForeignKey(
        'accountant.Account',
        related_name='destination_transactions'
    )

    def __unicode__(self):
        return unicode('%f %s -> %s' % (
            self.amount,
            self.source_account,
            self.destination_account
        ))

    def get_currency(self):
        """ Returns the currency of the destination account. """

        return self.get_destination_currency()
    currency = property(get_currency)

    def get_destination_currency(self):
        """ Returns the currency of the destination account. """

        return self.destination_account.currency
    destination_currency = property(get_destination_currency)

    def get_source_currency(self):
        """ Returns the currency of the source account. """

        return self.destination_account.currency
    source_currency = property(get_source_currency)


class AccountUserProfileMixin(object):
    """ Gives the user profile object access to the user accounts. """

    def get_accounts(self, only_primaries=True):
        """ Returns all accounts for the user. """

        return self.user.accounts.filter(
            models.Q(is_primary_destination=True),
            models.Q(is_primary_destination=True))
