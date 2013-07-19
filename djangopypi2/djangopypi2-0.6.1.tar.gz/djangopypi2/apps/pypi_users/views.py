from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

class SingleUserMixin(SingleObjectMixin):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    # avoid clash with 'user' from django.contrib.auth.context_processors.auth
    context_object_name = 'user_'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SingleUserMixin, self).dispatch(*args, **kwargs)

class MultipleUsersMixin(MultipleObjectMixin):
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'users'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MultipleUsersMixin, self).dispatch(*args, **kwargs)

class Index(MultipleUsersMixin, ListView):
    template_name = 'pypi_users/index.html'

class UserDetails(SingleUserMixin, DetailView):
    template_name = 'pypi_users/user_profile.html'
