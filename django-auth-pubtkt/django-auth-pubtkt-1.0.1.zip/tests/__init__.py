__author__ = 'Alexander Vyushkov'
#__version__ = ..django_auth_pubtkt.__version__
from django.test import TestCase
from django_auth_pubtkt import DjangoAuthPubtkt

class DjangoAuthPubtktTest (TestCase):
    def setUp(self):
        self.djangoAuthPubtkt = DjangoAuthPubtkt()
        self.request = ""

if __name__ == "__main__":
    pass
