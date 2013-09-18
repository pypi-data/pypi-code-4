# Copyright 2013 Binary Birch Tree
# http://www.binarybirchtree.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth import views as django_auth_views

from views import ProfileFormView, SignupFormView, ActivationView, combined_signup_login
from models import ACTIVATION_CODE_REGEX

urlpatterns = patterns(
	'',

	url(r'^profile/edit/$', login_required(ProfileFormView.as_view()), name='accounts_profile_edit'),
	url(r'^profile/$', login_required(TemplateView.as_view(template_name='accounts/profile_summary.html')), name='accounts_profile_home'),

	url(r'^activate/(?P<activation_code>' + ACTIVATION_CODE_REGEX + r')/$', ActivationView.as_view(), name='accounts_activation'),

	url(r'^signup/success/$', TemplateView.as_view(template_name='accounts/signup_success.html'), name='accounts_signup_success'),
	url(r'^signup/$', SignupFormView.as_view(), name='accounts_signup_form'),

	url(r'^login/$', django_auth_views.login, {'template_name': 'auth/login.html'}, name='auth_login'),
	url(r'^logout/$', django_auth_views.logout, {'template_name': 'auth/logged_out.html'}, name='auth_logout'),

	url(r'^password/change/$', django_auth_views.password_change, {'template_name': 'auth/password_change_form.html'}, name='auth_password_change'),
	url(r'^password/change/done/$', django_auth_views.password_change_done, {'template_name': 'auth/password_change_done.html'}, name='auth_password_change_done'),

	url(r'^password/reset/$', django_auth_views.password_reset, {'template_name': 'auth/password_reset_form.html', 'email_template_name': 'auth/password_reset_email.html', 'subject_template_name': 'auth/password_reset_subject.txt'}, name='auth_password_reset'),
	url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', django_auth_views.password_reset_confirm, {'template_name': 'auth/password_reset_confirm.html'}, name='auth_password_reset_confirm'),
	url(r'^password/reset/complete/$', django_auth_views.password_reset_complete, {'template_name': 'auth/password_reset_complete.html'}, name='auth_password_reset_complete'),
	url(r'^password/reset/done/$', django_auth_views.password_reset_done, {'template_name': 'auth/password_reset_done.html'}, name='auth_password_reset_done'),

	# This is a combined signup and login form that redirects to the profile page if the user is already logged in.
	url(r'^$', combined_signup_login, name='signup_login_form'),
)