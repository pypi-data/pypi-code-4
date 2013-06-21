"""
.. codeauthor:: Artur Barseghyan <artur.barseghyan@gmail.com>
"""

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from sirep.models import TestModel
from sirep.conf import get_setting

SHOW_ADMIN_TEST_MODEL_DEMO = get_setting('SHOW_ADMIN_TEST_MODEL_DEMO')

class TestModelAdmin(admin.ModelAdmin):
    """
    Admin for TestModel model. Part of sirep report implementation example.
    """
    list_display = ('title', 'counter', 'user')
    list_select_related = True

    list_per_page = 50

    class Meta:
        app_label = _('Test sirep model')

if SHOW_ADMIN_TEST_MODEL_DEMO:
    admin.site.register(TestModel, TestModelAdmin)
