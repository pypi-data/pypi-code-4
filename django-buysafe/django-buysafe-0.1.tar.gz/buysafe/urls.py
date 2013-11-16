from django.conf.urls import patterns, url


urlpatterns = patterns(
    'buysafe.views',
    url(r'^entry/(?P<order_id>\d+)/$', 'entry', name='buysafe_pay'),
    url(r'^start/$', 'start', name="buysafe_start"),
    (r'^success/(?P<payment_type>[01])/$', 'success'),
    (r'^fail/(?P<payment_type>[01])/$', 'fail'),
    (r'^check/(?P<payment_type>[01])/$', 'check')
)
