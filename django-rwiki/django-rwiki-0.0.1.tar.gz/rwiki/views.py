# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from datetime import datetime
from django.http import Http404
import urllib
from reversion.helpers import generate_patch_html
import reversion

import models as mymodels
import forms as myforms

from django.conf import settings as conf

from django.views.generic import DetailView, FormView, UpdateView, DeleteView


class PageDetailView(DetailView):

    template_name = "rwiki/default.html"
    context_object_name = "page"

    def __init__(self):
        pass

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            if (self.kwargs['slug']):
                return HttpResponseRedirect(reverse_lazy('app_wiki-add') +
                    "?%s" % urllib.urlencode({'ruta': self.kwargs['slug']}))
            else:
                return redirect('app_wiki-add')
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self):
        if (not self.kwargs['slug']):
            self.kwargs['slug'] = 'start'
        try:
            obj = mymodels.Page.objects.get(slug=self.kwargs['slug'], status=1)
        except:
            try:
                obj = mymodels.Page.objects.get(slug=self.kwargs['slug']+'/start', status=1)
            except:
                raise Http404
        if obj.public:
            return obj
        else:
            if self.request.user.is_superuser:
                return obj
            else:
                raise Http404
        #return obj
        #return get_object_or_404(mymodels.Page, slug=self.kwargs['slug'], status=1)

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        try:
            history = reversion.get_unique_for_object(self.object)
            last = history[0]
            for h in history:
                h.patch = generate_patch_html(last, h, "text", cleanup="semantic")
        except:
            history = ''

        breadcrumb = self.object.slug.split('/')
        breadcrumbs = {}
        for b in breadcrumb[:-1]:
            try:
                bread = mymodels.Page.objects.get(slug=b, status=1)
                breadcrumbs[b] = bread.slug
            except:
                try:
                    bread = mymodels.Page.objects.get(slug="%s/start" % b, status=1)
                    breadcrumbs[b] = bread.slug
                except:
                    breadcrumbs[b] = ''
        context.update({
            'history': history,
            'breadcrumbs': breadcrumbs,
            'last': breadcrumb[-1],
        })
        return context

    def get_template_names(self):
        """
         `get_object` has already set this attribute, so we pick up the
         template from the model. I it doesn't exists we pick up the
         super name.
        """
        try:
            templates = [self.object.template]
            return templates + super(PageDetailView, self).get_template_names()
        except:
            return super(PageDetailView, self).get_template_names()


class PageAdd(FormView):

    """
    Class Based View, add a new page.
    """

    form_class = myforms.PageForm
    template_name = 'rwiki/page_form.html'

    def get_initial(self):
        try:
            return { 'slug': self.request.GET['ruta'] }
        except:
            pass

    def get_success_url(self):
        return reverse_lazy('app_wiki-detail', args=(self.returnpath, ))

    def dispatch(self, *args, **kwargs):
        return super(PageAdd, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.returnpath = form.cleaned_data['slug']
        newpage = mymodels.Page( title = form.cleaned_data['title'],
                                 slug = form.cleaned_data['slug'],
                                 created = datetime.now(),
                                 text = form.cleaned_data['text'],
                                 hits = 1,
                                 status = form.cleaned_data['status'],
                                 template = form.cleaned_data['template'],
                                 owner = self.request.user)
        with reversion.create_revision():
            newpage.save()
            reversion.set_user(self.request.user)
            reversion.set_comment(form.cleaned_data['comment'])
        return super(PageAdd, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PageAdd, self).get_context_data(**kwargs)
        return context


class PageUpdate(UpdateView):

    """
    Class Based View, add a new page.
    """

    form_class = myforms.PageForm
    template_name = 'rwiki/page_form.html'

    def get_success_url(self):
        return reverse_lazy('app_wiki-detail', args=(self.kwargs['slug'], ))

    def get_object(self):
        self.obj = get_object_or_404(mymodels.Page, slug=self.kwargs['slug'], status=1)
        return self.obj

    def form_valid(self, form):
        with reversion.create_revision():
            reversion.set_user(self.request.user)
            reversion.set_comment(form.cleaned_data['comment'])
            form.instance.save()
        return super(PageUpdate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(PageUpdate, self).get_context_data(**kwargs)
        return context


def revert(request, objid, revid):
    page = get_object_or_404(mymodels.Page, id=objid, status=1)
    history = reversion.get_unique_for_object(page)
    for h in history:
        if str(h.revision_id) == str(revid):
            h.revision.revert()
    return redirect('app_wiki-detail', page.slug)


class PageDel(DeleteView):

    """
    Class Based View, delete page.
    """

    form_class = myforms.PageForm
    context_object_name = "page"

    def get(self, request, *args, **kwargs):
        self.obj = get_object_or_404(mymodels.Page, slug=self.kwargs['slug'])
        self.obj.delete()
        return redirect('app_wiki-detail', 'start')