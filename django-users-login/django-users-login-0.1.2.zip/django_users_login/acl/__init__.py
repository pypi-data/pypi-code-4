#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
from functools import wraps
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django_users_login.settings import VIRTUAL_DELETION

__author__ = 'Geraldo Andrade (geraldo@geraldoandrade.com)'


class ACO(models.Model):
    """
    ACO - Access Control Object
    ===========================

    An action that are requested to be performed.

    For example: edit a record, access some view, execute some method in model. All these mentioned is an action to be
    performed.

    More deeply: this is the object for all things that you want to control access. You MUST create all ACO (object)
    before create AXO (action) and ARO (user).

    """
    name = models.CharField(verbose_name=_('name'), max_length=255)
    is_deleted = models.BooleanField(default=False, verbose_name=_('deleted'))

    @classmethod
    def create(self, object_name):
        """
        to create an object
        """
        new_object = ACO(name=object_name)
        new_object.save()

    def delete(self, *args, **kwargs):
        if VIRTUAL_DELETION:
            self.is_deleted = True
            self.save()
        else:
            super(ACO, self).delete(*args, **kwargs)


class AXO(models.Model):
    """
    AXO - Access Request Object
    ===========================

    An object that represents an action to perform on ACO. That means ALL SELF is an action, and an action must be
    executed in some ACO.
    """
    name = models.CharField(verbose_name=_('name'), max_length=255)
    is_deleted = models.BooleanField(default=False, verbose_name=_('deleted'))

    @classmethod
    def create(self, action_name, aco):
        """
        to create an object
        """
        new_object = AXO(name=action_name, aco)
        new_object.save()

    def delete(self, *args, **kwargs):
        if VIRTUAL_DELETION:
            self.is_deleted = True
            self.save()
        else:
            super(AXO, self).delete(*args, **kwargs)


class ARO(models.Model):
    """
    ARO - Access Request Object
    ===========================

    An entity (in this case a user) that is requesting an action to be performed.
    """
    user = models.ForeignKey(User)
    is_deleted = models.BooleanField(default=False, verbose_name=_('deleted'))

    def delete(self, *args, **kwargs):
        if VIRTUAL_DELETION:
            self.is_deleted = True
            self.save()
        else:
            super(ARO, self).delete(*args, **kwargs)


class ACL(object):
    """
    ACL - Access Control List
    =========================

    This is the representation of what user can do anything in a given area.

    """

    is_deleted = models.BooleanField(default=False, verbose_name=_('deleted'))

    aro = models.ForeignKey(ARO)
    axo = models.ForeignKey(AXO)
    aco = models.ForeignKey(ACO)

    @classmethod
    def check(cls, aro, axo, aco):
        """
        check
        -----

        This method checks if a user can do an action in some ``ARO``
        """

        if not aro:
            raise Exception('Cannot check ACL from nonusers')
            # great lets find axo and aco
            # TODO: i stop here


    @classmethod
    def add_rule(cls, aro, axo, aco):
        """
        add_rule
        --------

        Here we can add a rule. ARO (who), AXO (action), ACO (where).
        """
        if isinstance(aro, ARO) and isinstance(axo, AXO) and isinstance(aco, ACO):
            acl = ACL()
            acl.aco = aco
            acl.aro = aro
            acl.axo = axo
            try:
                acl.save()
            except Exception, e:
                raise Exception('Cannot save ACL object: %s' % e)
            acl.save()
        else:
            raise Exception('Malformed rule') # in this case all objects is required

            #def remove_rule_by_aco(self)


    @classmethod
    def register_rule(cls):
        pass


def check():
    """
    check
    =====

    Decorator to make a view executable only if ALC.check() pass.  Usage::

        @check(aco='', axo='')
        def my_view(request):
            # I can assume now that only GET or POST requests make it this far
            # ...

    Note that request methods should be in uppercase.
    """

    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):
            if request.method not in request_method_list:
                logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
                               extra={
                                   'status_code': 405,
                                   'request': request
                               }
                )
                return HttpResponseNotAllowed(request_method_list)
            return func(request, *args, **kwargs)

        return inner

    return decorator
