# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousOperation

from pytils.templatetags.pytils_translit import translify
from pytils.translit import RU_ALPHABET

EN_ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
               'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w',
               'x', 'y', 'z']
ALPHABET = RU_ALPHABET + EN_ALPHABET


class BalancedFileSystemStorage(FileSystemStorage):

    def prefix(self, file_name):
        for char in file_name.lower():
            if char not in ALPHABET:
                file_name = file_name.replace(char, 'a')
        file_name = translify(file_name).zfill(1)
        sub0 = file_name[0]
        if sub0 in [u'?', u'-', u'*', u'_', u' ']:
            sub0 = u'a'
        if len(file_name) == 1:
            sub1 = sub0
        else:
            sub1 = file_name[1]
            if sub1 in [u'?', u'-', u'*', u'_', u' ']:
                sub1 = u'a'
        return (sub0, sub1)

    def rel_path(self, name):
        name, file_name = os.path.split(name)
        sub0, sub1 = self.prefix(file_name)
        path = os.path.join(name, sub0, sub1, file_name)
        return os.path.normpath(path)

    def path(self, name):
        return super(BalancedFileSystemStorage,
                     self).path(self.rel_path(name))

    def url(self, name):
        return super(BalancedFileSystemStorage,
                     self).url(self.rel_path(name))


class StaticStorage(FileSystemStorage):
    def path(self, name):
        if not name.startswith(settings.STATIC_URL):
            return super(StaticStorage, self).path(name)

        name = name.replace(settings.STATIC_URL, '')
        path = os.path.join(settings.STATIC_ROOT, name.lstrip('/'))
        path = os.path.normpath(path)
        return path
                                