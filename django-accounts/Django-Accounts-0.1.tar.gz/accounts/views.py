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

from django.views.generic import FormView, TemplateView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import get_current_site
from django.contrib.auth import REDIRECT_FIELD_NAME

from forms import ProfileForm, SignupForm
from models import UserSignup


class ProfileFormView(FormView):
	form_class = ProfileForm
	template_name = 'accounts/profile_form.html'
	success_url = reverse_lazy('accounts_profile_summary')

	def get_initial(self):
		return {
		'first_name': self.request.user.first_name,
		'last_name': self.request.user.last_name,
		}

	def form_valid(self, form):
		self.request.user.first_name = form.cleaned_data['first_name']
		self.request.user.last_name = form.cleaned_data['last_name']
		self.request.user.save()

		return super(ProfileFormView, self).form_valid(form)

class SignupFormView(FormView):
	form_class = SignupForm
	template_name = 'accounts/signup_form.html'
	success_url = reverse_lazy('accounts_signup_success')

	def form_valid(self, form):
		UserSignup.objects.signup(form.cleaned_data)
		return super(SignupFormView, self).form_valid(form)

class ActivationView(TemplateView):
	http_method_names = ['get']
	template_name = 'accounts/activation.html'
	success_url = reverse_lazy('accounts_profile_home')

	def get(self, request, *args, **kwargs):
		if UserSignup.objects.activate(**kwargs):
			return redirect(self.success_url)

		return super(ActivationView, self).get(request, *args, **kwargs)

def combined_signup_login(request):
	if request.user.is_authenticated():
		return redirect('accounts_profile_home')

	return render(request, 'accounts/signup_login_form.html', {
		'signup_form': SignupForm(),
		'login_form': AuthenticationForm(request),
		REDIRECT_FIELD_NAME: request.REQUEST.get(REDIRECT_FIELD_NAME, ''),
		'site': get_current_site(request),
	})