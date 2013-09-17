from django.conf.urls import patterns, include, url
from django.contrib.auth.urls import urlpatterns as user_urlpatterns
from django.contrib.auth.decorators import login_required

from user.views import SignInView, SignUpView, ProfileView

urlpatterns = patterns('',
    url(r'^sign-in/$', SignInView.as_view(template_name='user/sign_in.html'), name='sign_in'),
    url(r'^sign-up/$', SignUpView.as_view(template_name='user/sign_up.html'), name='sign_up'),
    url(r'^profile/$', login_required(ProfileView.as_view(template_name='user/profile.html')), name='profile'),
)

urlpatterns += user_urlpatterns