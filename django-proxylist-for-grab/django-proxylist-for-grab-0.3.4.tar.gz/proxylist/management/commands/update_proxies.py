# -*- coding: utf-8 -*-

import os

from django.core.management.base import BaseCommand

from optparse import make_option

from proxylist.models import Proxy


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

    def get_data(self, line):
        line = line.strip()
        if '@' in line:
            proxy, auth = line.split('@', 2)
            return proxy.split(':') + auth.split(':')
        return line.split(':', 2) + ['', '']

    def handle(self, *args, **options):
        for filename in args:
            if not os.path.isfile(filename):
                self.stderr.write("File %s does not exists!\n" % filename)
                continue

            self.stdout.write("Loading %s...\n" % filename)

            with open(filename, 'r') as f:
                for proxy in f:
                    hostname, port, user, password = self.get_data(proxy)

                    try:
                        port = int(port)
                    except ValueError:
                        self.stderr.write("Invalid port %s value" % port)
                        continue

                    Proxy.objects.get_or_create(
                        hostname=hostname, port=port,
                        user=user, password=password,
                        proxy_type=options['type'])
