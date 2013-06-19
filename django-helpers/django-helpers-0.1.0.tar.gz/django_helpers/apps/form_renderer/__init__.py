# coding=utf-8
import urls

from renderer import FormRenderer
from bootstrap import BootstrapFormRenderer
from django_helpers import add_app_url

add_app_url('form-renderer/', urls)