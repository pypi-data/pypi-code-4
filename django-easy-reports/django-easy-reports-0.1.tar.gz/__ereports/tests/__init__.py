# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test.testcases import TestCase
from .models import Report

class EasyReportsTestCase(TestCase):
    def test_success(self):
        t = Report(name='Report1',
            target_model=ContentType.objects.get_for_model(User),
            published=False,
            headers='User',
            columns='username',
            filtering='',
            ordering=''
        )
        t.save()

    def test_wrong_filter(self):
        t = Report(name='Report1',
            target_model=ContentType.objects.get_for_model(User),
            published=False,
            headers='',
            columns='',
            filtering='aa',
            ordering=''
        )
        self.assertRaises(ValidationError, t.clean)

    def test_wrong_order(self):
        t = Report(name='Report1',
            target_model=ContentType.objects.get_for_model(User),
            published=False,
            headers='',
            columns='',
            filtering='',
            ordering='qqq'
        )
        self.assertRaises(ValidationError, t.clean)

#    def test_wrong_field(self):
#        t = Report(name='Report1',
#            target_model = ContentType.objects.get_for_model(User),
#            published = False,
#            headers = '',
#            columns = 'nofield',
#            filtering = '',
#            ordering = ''
#        )
#        self.assertRaises(ValidationError, t.clean)
