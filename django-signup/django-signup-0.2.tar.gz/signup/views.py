from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django.shortcuts import redirect

from .models import Validation, SIGNUP_FORM_CLASS

class SignUpView(FormView):
	template_name = 'registration/signup_form.html'
	success_url = reverse_lazy('signup_signup_complete')

	def get_form_class(self):
		if self.form_class is None:
			form_class_name = SIGNUP_FORM_CLASS
			if form_class_name is None:
				from .forms import DefaultUserCreationForm
				self.form_class = DefaultUserCreationForm
			else:
				import importlib
				module_name, class_name = form_class_name.rsplit('.', 1)
				module = importlib.import_module(module_name)
				self.form_class = getattr(module, class_name)

		return self.form_class
	
	def form_valid(self, form):
		user = Validation.objects.create_inactive_user(**form.cleaned_data)
		validation = Validation.objects.create_validation(user)

		validation.send_activation_email(get_current_site(self.request))

		return super(SignUpView, self).form_valid(form)

		
class SignUpCompleteView(TemplateView):
	template_name = 'registration/signup_complete.html'
	
class ActivateView(TemplateView):
	template_name = 'registration/activation_failed.html'

	def get(self, request, *args, **kwargs):
		try:
			validation = Validation.objects.get(key=kwargs['activation_key'])
			validation.activate_user()
			validation.delete()
			return redirect('signup_activate_complete')
		except Validation.DoesNotExist:
			pass

		return super(ActivateView, self).get(request, *args, **kwargs)
	
class ActivateCompleteView(TemplateView):
	template_name = 'registration/activation_complete.html'

