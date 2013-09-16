from django.conf.urls.defaults import *
from django.contrib.auth.urls import urlpatterns as user_urlpatterns

from user.views import SignUpView

urlpatterns = patterns('',
    url(r'^sign-up/$', SignUpView.as_view(template_name='user/sign_up.html'), name='sign_up'),
)

urlpatterns += user_urlpatterns