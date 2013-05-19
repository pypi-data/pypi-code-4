from django.conf import settings

from radpress.tests.base import BaseTest, RestructuredtextTest
from radpress.tests.md import MarkdownTest

if 'django.contrib.admin' in settings.INSTALLED_APPS:
    from radpress.tests.admin import AdminTest
else:
    print("`django.contrib.admin` is not installed, passed admin tests...")
