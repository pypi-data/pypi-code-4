# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.utils import unittest

class TestCase(unittest.TestCase):

    def setUp(self):
        self.user = User.objects.create(
            id=1,
            username='dumbledore',
            first_name='Albus Percival Wulfric Brian',
            last_name='Dumbledore'
        )

    def tearDown(self):
        self.user.delete()