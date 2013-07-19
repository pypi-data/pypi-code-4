from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.forms.models import inlineformset_factory
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from ..pypi_metadata.models import Classifier
from ..pypi_ui.shortcuts import render_to_response

from .decorators import user_maintains_package, user_owns_package
from .models import Package, Release
from .forms import SimplePackageSearchForm, AdvancedPackageSearchForm

class Index(ListView):
    model = Package
    context_object_name = 'packages'

    def get_queryset(self):
        if 'query' in self.request.GET:
            q = self.request.GET['query']
            return Package.simple_search(q)
        return Package.objects.all()

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['search_form'] = SimplePackageSearchForm(self.request.GET)
        return context

def advanced_search(request):
    if request.method == 'POST':
        form = AdvancedPackageSearchForm(request.POST)
        if form.is_valid():
            qname = form.cleaned_data['name']
            qsummary = form.cleaned_data['summary']
            qdescription = form.cleaned_data['description']
            qclassifier = set(form.cleaned_data['classifier'])
            qkeyword = set(form.cleaned_data['keywords'].split())
            result = Package.advanced_search(qname, qsummary, qdescription, qclassifier, qkeyword)
    else:
        form = AdvancedPackageSearchForm()
        result = None
    return render(request, 'pypi_packages/package_search.html', {
        'search_form': form,
        'search_result': result
    })

class SinglePackageMixin(SingleObjectMixin):
    model = Package
    context_object_name = 'package'
    slug_url_kwarg = 'package_name'
    slug_field = 'name'

class PackageDetails(SinglePackageMixin, DetailView):
    pass

class PackagePermission(SinglePackageMixin, UpdateView):
    template_name = 'pypi_packages/package_permission.html'

    def post(self, request, *args, **kwargs):
        package = self.get_object()
        if request.user not in package.owners.all():
            return HttpResponseForbidden()

        user = get_object_or_404(User, username__exact = self.request.POST['username'])
        action = self.request.POST['action']
        relation = self.request.POST['relation']
        if action == 'add':
            if relation == 'owner':
                package.owners.add(user)
            elif relation == 'maintainer':
                package.maintainers.add(user)
        elif action == 'delete':
            if relation == 'owner':
                if package.owners.count() == 1:
                    return HttpResponseForbidden()
                package.owners.remove(user)
            elif relation == 'maintainer':
                package.maintainers.remove(user)
        return HttpResponse()

class DeletePackage(SinglePackageMixin, DeleteView):
    success_url = reverse_lazy('djangopypi2-packages-index')

    @method_decorator(user_owns_package())
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeletePackage, self).dispatch(request, *args, **kwargs)
