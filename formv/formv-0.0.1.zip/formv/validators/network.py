#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import dns.exception, socket
from dns import ipv4, ipv6
from formv.validators.strings import VString
from formv.exception import Invalid
from formv.utils import extract_text as _

__all__ = ('VIPAddress','VCIDR','VMACAddress',)

class VIPAddress(VString):
    def _validate(self, value):
        value = VString._validate(self, value)
        self.messages.update({'invalid': _('Invalid IP address: %(ipaddr)s')})
        
        try:
            value = ipv4.inet_ntoa(ipv4.inet_aton(value))
        except (dns.exception.DNSException, socket.error):
            try:
                value = ipv6.inet_ntoa(ipv6.inet_aton(value))
            except (dns.exception.DNSException, socket.error):
                raise Invalid(self.message('invalid', ipaddr=value), value)
        return value


class VCIDR(VString):
    def _validate(self, value):
        value = VString._validate(self, value)
        self.messages.update({'invalid': _('Invalid CIDR format: %(format)s')})

        try:
            ip, size = value, '32'
            if '/' in value: 
                ip, size = value.split('/')
            if not 0 <= int(size) <= 32:
                raise Invalid(self.message('invalid', format=value), value)
            ip = ipv4.inet_ntoa(ipv4.inet_aton(ip))
            return (ip + '/' + size)        
        except (dns.exception.DNSException, socket.error):
            try:
                ip, size = value, '64'
                if '/' in value: 
                    ip, size = value.split('/')
                if not 0 <= int(size) <= 64:
                    raise Invalid(self.message('invalid', format=value), value)
                ip = ipv6.inet_ntoa(ipv6.inet_aton(ip))
                return (ip + '/' + size)
            except (dns.exception.DNSException, socket.error):
                raise Invalid(self.message('invalid', format=value), value)    


class VMACAddress(VString):
    def _validate(self, value):
        value = VString._validate(self, value).upper()
        self.messages.update({'invalid': _('Invalid MAC address: %(macaddr)s')})
        
        allowed = '0123456789ABCDEF'
        for c in (' ',':','-','.'):
            value = value.replace(c, '')
        if len(value) != 12:
            raise Invalid(self.message('invalid', macaddr=value), value)
        if [k for k in set(value) if k not in allowed]:
            raise Invalid(self.message('invalid', macaddr=value), value)
        return '%s:%s:%s:%s:%s:%s' % (value[0:2], value[2:4], value[4:6],
                                      value[6:8], value[8:10], value[10:12])