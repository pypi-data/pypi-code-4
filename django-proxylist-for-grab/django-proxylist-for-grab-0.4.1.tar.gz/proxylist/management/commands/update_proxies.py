# -*- coding: utf-8 -*-

import os

from django.core.management.base import BaseCommand

from optparse import make_option

from proxylist.models import Proxy


class ProcessFile(object):
    def __init__(self, filename, proxy_type='http'):
        self.filename = filename
        self.proxy_type = proxy_type

    def get_data(self, line):
        line = line.strip()
        if '@' in line:
            proxy, auth = line.split('@', 2)
            return proxy.split(':') + auth.split(':')
        return line.split(':', 2) + ['', '']

    def save(self, hostname, port, user, password):
        Proxy.objects.get_or_create(
            hostname=hostname, port=port, user=user, password=password,
            proxy_type=self.proxy_type
        )

    def run(self):
        with open(self.filename) as f:
            for proxy in f:
                self.save(*self.get_data(proxy))


class Command(BaseCommand):
    args = '<hidemyass proxy list files>'
    help = 'Update proxy list from file(s)'

    option_list = BaseCommand.option_list + (
        make_option(
            '--type',
            dest='type',
            default='http',
            help='http, https, socks4, socks5'),
    )

    def handle(self, *args, **options):
        for filename in args:
            if not os.path.isfile(filename):
                self.stderr.write("File %s does not exists!\n" % filename)
                continue

            self.stdout.write("Loading %s...\n" % filename)

            ProcessFile(filename, options['type']).run()
