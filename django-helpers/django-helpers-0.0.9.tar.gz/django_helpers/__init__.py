# coding=utf-8
import collections
from django.conf.urls import include, url
from urls import urlpatterns


def add_app_url(name, urls):
    reg_exp = r'^%s/' % name
    name += '-urls'

    for pattern in urlpatterns:
        if pattern._regex == reg_exp:
            return

    pattern = url(reg_exp, include(urls), name=name)
    urlpatterns.append(pattern)


def get_settings_val(name, default=None):
    from django.conf import settings

    obj = getattr(settings, name, default)
    return obj


def check_settings_val_exist(name, tolerate_blank=False, tolerate_spaces=True):
    val = get_settings_val(name)
    if val is None:
        raise Exception('Missing settings value: %s' % name)

    if (not tolerate_blank and val) == '' or (not tolerate_spaces and val.isspace()):
        raise Exception('Improperly configured settings value: %s' % name)


def is_func(obj):
    return hasattr(obj, '__call__')


def is_list(obj):
    if isinstance(obj, basestring):
        return False
    return isinstance(obj, collections.Sequence)


def convert_js_bool(o):
    if o:
        return 'true'
    return 'false'


def create_attr_from_obj(obj, ignore_function=True, ignore_lists=True, js_bool=True):
    attrs = dir(obj)
    d = {}
    for attr in attrs:
        val = getattr(obj, attr)
        if ignore_function and is_func(val):
            continue

        if ignore_lists and is_list(val):
            continue

        if val is True or val is False:
            val = convert_js_bool(val)

        d[attr] = val

    return d


#
#   Code Copied from https://github.com/un33k/django-ipware/blob/master/ipware/ip.py
#

import socket


def is_valid_ip(ip_address):
    """ Check Validity of an IP address """
    valid = True
    try:
        socket.inet_aton(ip_address.strip())
    except:
        valid = False
    return valid


def get_ip_address_from_request(request):
    """ Makes the best attempt to get the client's real IP or return the loopback """

    PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', '127.' )
    ip_address = ''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded_for and ',' not in x_forwarded_for:
        if not x_forwarded_for.startswith(PRIVATE_IPS_PREFIX) and is_valid_ip(x_forwarded_for):
            ip_address = x_forwarded_for.strip()
    else:
        ips = [ip.strip() for ip in x_forwarded_for.split(',')]
        for ip in ips:
            if ip.startswith(PRIVATE_IPS_PREFIX):
                continue
            elif not is_valid_ip(ip):
                continue
            else:
                ip_address = ip
                break
    if not ip_address:
        x_real_ip = request.META.get('HTTP_X_REAL_IP', '')
        if x_real_ip:
            if not x_real_ip.startswith(PRIVATE_IPS_PREFIX) and is_valid_ip(x_real_ip):
                ip_address = x_real_ip.strip()
    if not ip_address:
        remote_addr = request.META.get('REMOTE_ADDR', '')
        if remote_addr:
            if not remote_addr.startswith(PRIVATE_IPS_PREFIX) and is_valid_ip(remote_addr):
                ip_address = remote_addr.strip()
    if not ip_address:
        ip_address = '127.0.0.1'
    return ip_address


#
#   End copied code
#