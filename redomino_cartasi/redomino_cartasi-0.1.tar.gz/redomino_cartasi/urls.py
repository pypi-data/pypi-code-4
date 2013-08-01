from django.conf.urls.defaults import *

urlpatterns = patterns('redomino_cartasi.views',
#            url(r'^cartasi$', 'cartasi', name="cartasi"),
            url(r'^postform_cartasi$', 'postform_cartasi', name="postform_cartasi"),
            url(r'^paid_cartasi$', 'paid_cartasi', name="paid_cartasi"),
            url(r'^error$', 'error', name="error"),
            url(r'^annulment$', 'annulment', name="annulment"),
            url(r'^thank-you', "thank_you", name="lfs_thank_you")
            )

