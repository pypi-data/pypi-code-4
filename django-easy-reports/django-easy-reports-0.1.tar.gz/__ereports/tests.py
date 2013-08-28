# -*- coding: utf-8 -*-
from contextlib import contextmanager
import functools
import random
from django.contrib.auth.models import Permission, Group
from django.core.urlresolvers import reverse
from django.db.models import Q
from django_dynamic_fixture import G
from django_webtest import WebTest
from pasportng.pasport.models import PEmployee, PUser
from pasportng.pasport.models.office import PasportOffice
from pasportng.wings.models import Country
from wfp_djangolib.utils.test import rnd
from wfp_djangolib.utils.test.any import R
from wfp_djangolib.utils.test.rnd import text, unique


def wfp_user(password=None, permissions=[], groups=[], **kwargs):
    is_active = kwargs.pop('is_active', True)
    is_superuser = kwargs.pop('is_superuser', False)
    is_staff = kwargs.pop('is_staff', False)

    user = G(PUser, is_active=is_active, is_superuser=is_superuser,
             is_staff=is_staff, **kwargs)

    for group_name in groups:
        group = Group.objects.get(name=group_name)
        user.groups.add(group)

    for permission_name in permissions:
        app_label, codename = permission_name.split('.')
        permission = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename)
        user.user_permissions.add(permission)

    if password:
        user.set_password(password)

    user.save()
    return user


def wfp_group(name=None, permissions=[]):
    group = G(Group, name=(name or text(10)))
    for permission_name in permissions:
        app_label, codename = permission_name.split('.')
        permission = Permission.objects.get(
            content_type__app_label=app_label,
            codename=codename)
        group.permissions.add(permission)
    return group


# wfp_country = functools.partial(G, Country,
#                                 # iso_code=lambda x: rnd.iso2(),
#                                 # iso3_code=lambda x: rnd.iso3(),
#                                 num_code=lambda x: rnd.isonum(),
#                                 fullname=lambda x: rnd.text(10),
#                                 name=lambda x: rnd.text(10))
#

wfp_office = functools.partial(G, PasportOffice,
                               # country=lambda x: R(Country, u=True),
                               # type=lambda x: choice(PasportOffice.TYPE)[0],
                               code=lambda x: unique(rnd.office_code)(),
                               name=lambda x: rnd.name())


@contextmanager
def user_add_permission(user, permissions):
    """
        temporary add permissions to user

    :param user:
    :param permissions: list
    :return:

    >>> u = PUser()
    >>> with user_add_permission(u, ['test']):
    ...     u.has_perm('test')
    True
    """
    old = Permission.objects.select_related('user', 'user__groups').filter(Q(user=user) | Q(group__in=user.groups.all()))
    if hasattr(user, '_perm_cache'):
        del user._perm_cache
    new_perms = []
    for perm_name in permissions:
        app_label, code = perm_name.split('.')

        perm = Permission.objects.get(codename=code, content_type__app_label=app_label)
        user.user_permissions.add(perm)
        new_perms.append(perm)
    yield
    for p in new_perms:
        user.user_permissions.remove(p)
    del user._perm_cache


def wfp_pasport_employee(**kwargs):
    """
        wfpemployee(offices=[(Office1, SC),(Office2, SS)])

    :param kwargs:
    :return:
    """
    n = kwargs.pop('n', 1)
    created = []
    for i in range(n):
        params = {'index_no': lambda x: rnd.num(10),
                  'last_name': lambda x: rnd.name(),
                  'first_name': lambda x: rnd.name(),
                  'nickname': lambda x: rnd.text(10),
                  'email': lambda x: rnd.email()}
        params.update(kwargs)
        offices = params.pop('offices', [])
        e = G(PEmployee, **params)
        created.append(e)
    return created


wfp_contract_type = lambda x: random.choice('SSA', 'SC')


class EreportTest(WebTest):
    fixtures = ['initial_reports.json']

    def setUp(self):
        super(EreportTest, self).setUp()
        # wfp_country(5)
        offices = wfp_office(n=2)
        self.office = offices[0]
        self.no_access_office = offices[1]
        e = wfp_pasport_employee(offices=[(self.office, lambda x: wfp_contract_type(x))], n=10)
        self.employee = e[0]
        self.user = wfp_user()

    def test_nav(self):
        url = reverse('pasport.views.office.index', args=[self.office.code])
        # url = reverse('pasport.views.office.index', args=[self.office.code])
        print 111, url, self.user, type(self.user)
        # url = reverse('ereports.list_office_reports', args=[self.office.code])
        # with user_add_office_permission(self.user, self.office, ['billing.list_employee']):
        res = self.app.get(url, user=self.user)
        res.showbrowser()
        # res = res.click(self.office.name)
        # res = res.click('Employees')
        # res.showbrowser()

        # with user_add_office_permission(self.user, self.office, ['billing.view_employee']):
        # res = res.click(self.employee.index_no)