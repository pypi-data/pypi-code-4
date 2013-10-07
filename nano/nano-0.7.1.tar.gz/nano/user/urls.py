from django.conf.urls.defaults import *

signup_done_data = { 'template_name': 'nano/user/signup_done.html' }

# 'project_name' should be a setting
password_reset_data = {'project_name': 'CALS'}

urlpatterns = patterns('nano.user.views',
    (r'^signup/$',          'signup', {}, 'nano_user_signup'),
    (r'^password/reset/$',  'password_reset', password_reset_data, 'nano_user_password_reset'),
    (r'^password/change/$', 'password_change', {}, 'nano_user_password_change'),
)

urlpatterns += patterns('',
    url(r'^signup/done/$', 'django.shortcuts.render', signup_done_data, name='nano_user_signup_done'),
)
