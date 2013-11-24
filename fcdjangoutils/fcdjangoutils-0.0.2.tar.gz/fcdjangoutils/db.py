# -*- coding: utf-8 -*-

from django.db import transaction

class Transaction(object):
    def __init__(self, db=None):
        self.db = db
        self.done = False

    def __enter__(self):
        print "Entering a transaction"
        transaction.enter_transaction_management(using=self.db)
        transaction.managed(True, using=self.db)
        return self

    def __exit__(self, a,b,c):
        if a is None:
            self.commit()
        else:
            self.rollback()

            
    def rollback(self):
        # TODO: Might be nice to log all DB rollbacks...
        if self.done:
            return
        self.done = True
        transaction.rollback(using=self.db)
        transaction.leave_transaction_management(using=self.db)
        print "Rolling back"

    def commit(self):
        if self.done:
            return
        self.done = True
        transaction.commit(using=self.db)
        transaction.leave_transaction_management(using=self.db)
        print "Commiting"

