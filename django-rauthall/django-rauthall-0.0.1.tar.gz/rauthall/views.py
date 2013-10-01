# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
import models as mymodels
import forms as myforms

from django.conf import settings as conf

from django.views.generic import UpdateView


class UserProfile(UpdateView):

    """
    Class Based View UserProfile.
    """

    model = mymodels.UserProfile
    form_class = myforms.ProfileForm
    template_name = "rauthall/profile.html"
    #context_object_name = "myuser"

    def get_success_url(self):
        return reverse_lazy('app_rauthall-profile')

    def get_object(self):
        #print self.request.user
        self.obj = get_object_or_404(mymodels.UserProfile, user=self.request.user)
        return self.obj

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserProfile, self).dispatch(*args, **kwargs)


    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(UserProfile, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(UserProfile, self).get_context_data(**kwargs)
        title = _('User Profile')
        userprofile = get_object_or_404(mymodels.UserProfile, user=self.request.user)
        context.update({
            'title': title,
            'userprofile': userprofile,
        })
        return context