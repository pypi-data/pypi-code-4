from django.conf.urls.defaults import *

from user.views import SignInView, SignUpView

urlpatterns = patterns('',
    url(r'^sign-in/$', SignInView.as_view(template_name='user/sign_in.html'), name='sign_in'),
    url(r'^sign-up/$', SignUpView.as_view(template_name='user/sign_up.html'), name='sign_up'),
)
