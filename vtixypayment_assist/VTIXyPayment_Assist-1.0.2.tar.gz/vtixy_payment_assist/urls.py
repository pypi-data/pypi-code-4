from django.conf.urls import patterns, url


urlpatterns = patterns('',
                       url(r'^confirm/', 'vtixy_payment_assist.views.confirm'),
                       url(r'^orderstate/(?P<order_id>[0-9]+)/$', 'vtixy_payment_assist.views.check'),
                       )
