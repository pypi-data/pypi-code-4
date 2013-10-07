from django.conf.urls.defaults import *

urlpatterns = patterns('nano.faq.views',
        (r'^$',                     'list_faqs'),
)
