# coding=utf-8

from django_helpers import add_app_url
import urls

add_app_url('auto-complete', urls)

from autocomplete import AutoComplete
from views import register
