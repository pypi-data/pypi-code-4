import json

from django.views.generic.base import View, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, UpdateView, DeleteView, DetailView, CreateView
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib import messages
from django.db.models import Max
from django.http import HttpResponse, Http404

from braces.views import JSONResponseMixin, LoginRequiredMixin, CsrfExemptMixin

from ftp_deploy.conf import *
from ftp_deploy.models import Service, Log
from ftp_deploy.utils.curl import curl_connection
from ftp_deploy.utils.core import commits_parser, absolute_url
from .forms import ServiceForm


class DashboardView(LoginRequiredMixin, ListView):

    """View for dashboard"""

    model = Service
    queryset = Service.objects.all().select_related().order_by("status", "-log__created").annotate(date=Max('log__created'))
    context_object_name = 'services'
    template_name = "ftp_deploy/dashboard.html"
    paginate_by = 25

    def post(self, request, *args, **kwargs):
        services = self.get_queryset()
        if self.request.POST['services']:
            services = services.filter(pk=self.request.POST['services'])
        return render_to_response('ftp_deploy/service/list.html', locals(), context_instance=RequestContext(request))


class ServiceManageView(LoginRequiredMixin, DetailView):

    """View for manage services"""

    model = Service
    context_object_name = 'service'
    template_name = "ftp_deploy/service/manage.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceManageView, self).get_context_data(**kwargs)
        context['recent_logs'] = self.get_object().log_set.all()[:15]
        context['fail_logs'] = self.get_object().log_set.filter(status=0).filter(skip=0)
        return context


class ServiceAddView(LoginRequiredMixin, CreateView):

    """View for add serives"""

    model = Service
    form_class = ServiceForm
    success_url = reverse_lazy('ftpdeploy_dashboard')
    template_name = "ftp_deploy/service/form.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceAddView, self).get_context_data(**kwargs)
        context['title'] = 'Add Service'
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Service has been added.')
        return super(ServiceAddView, self).form_valid(form)


class ServiceEditView(LoginRequiredMixin, UpdateView):

    """View for edit services"""

    model = Service
    form_class = ServiceForm
    template_name = "ftp_deploy/service/form.html"

    def get_success_url(self):
        return reverse('ftpdeploy_service_manage', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super(ServiceEditView, self).get_context_data(**kwargs)
        context['title'] = 'Edit Service'
        return context

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, 'Service has been updated.')
        return super(ServiceEditView, self).form_valid(form)


class ServiceDeleteView(LoginRequiredMixin, DeleteView):

    """View for delete services"""

    model = Service
    success_url = reverse_lazy('ftpdeploy_dashboard')
    template_name = "ftp_deploy/service/delete.html"

    def delete(self, request, *args, **kwargs):
        messages.add_message(request, messages.SUCCESS, 'Service has been removed.')
        return super(ServiceDeleteView, self).delete(request, *args, **kwargs)


class ServiceStatusView(JSONResponseMixin, LoginRequiredMixin, SingleObjectMixin, View):

    """View for update(save) and check service status"""

    model = Service

    def post(self, request, *args, **kwargs):
        service = self.get_object()
        service.save()
        response = request.POST.get('response', '')

        if response == 'list':
            services = list()
            services.append(service)
            return render_to_response('ftp_deploy/service/list.html', locals(), context_instance=RequestContext(request))

        if response == 'manage':
            recent_logs = service.log_set.all()[:15]
            fail_logs = service.log_set.filter(status=0).filter(skip=0)
            return render_to_response('ftp_deploy/service/manage.html', locals(), context_instance=RequestContext(request))

        if response == 'json':
            context = {
                'status': service.status,
                'status_message': service.status_message,
                'updated': service.updated
            }
            return self.render_json_response(context)

        raise Http404


class ServiceRestoreView(LoginRequiredMixin, DetailView):

    """"View for build restore path for service"""

    model = Service
    prefetch_related = ["log_set"]
    template_name = "ftp_deploy/service/modal.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceRestoreView, self).get_context_data(**kwargs)

        logs = self.get_logs_tree()

        context['payload'] = json.loads(logs[0].payload)
        context['payload']['user'] = 'Restore'
        context['service'] = self.get_object()

        commits = list()
        for log in logs:
            payload = json.loads(log.payload)
            commits += payload['commits']

        context['payload']['commits'] = commits
        context['payload'] = json.dumps(context['payload'])

        context['files_added'], context['files_modified'], context['files_removed'] = commits_parser(commits).file_diff()
        context['commits_info'] = commits_parser(commits).commits_info()

        return context

    def post(self, request, *args, **kwargs):

        if request.POST['payload']:
            self.get_logs_tree().delete()

        return HttpResponse(reverse('ftpdeploy_deploy', args=(self.get_object().secret_key,)))

    def get_logs_tree(self):
        """get logs tree for restore deploys. Include all logs since first fail apart of skiped."""
        first_fail_log = self.get_object().log_set.filter(status=0).filter(skip=0).order_by('pk')[:1]
        logs = self.get_object().log_set.filter(skip=0).filter(pk__gte=first_fail_log[0].pk).order_by('pk')
        return logs


class LogView(LoginRequiredMixin, ListView):

    """View for display logs"""

    model = Log
    context_object_name = 'logs'
    template_name = "ftp_deploy/log/log.html"
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(LogView, self).get_context_data(**kwargs)
        context['service_list'] = Service.objects.all().values('repo_name', 'pk')
        return context

    def post(self, request, *args, **kwargs):
        logs = self.get_queryset()
        if self.request.POST['services']:
            logs = logs.filter(service__pk=self.request.POST['services'])

        if not int(self.request.POST['status']):
            logs = logs.filter(status=self.request.POST['status'])

        return render_to_response('ftp_deploy/log/list.html', locals(), context_instance=RequestContext(request))


class LogSkipDeployView(LoginRequiredMixin, JSONResponseMixin, SingleObjectMixin, View):

    """View for skip fail logs"""

    model = Log

    def post(self, request, *args, **kwargs):
        log = self.get_object()
        log.skip = 1
        log.save()
        return self.render_json_response({'status': 'success'})


class BitbucketAPIView(LoginRequiredMixin, JSONResponseMixin, SingleObjectMixin, View):

    """View for managing BitBucket API"""

    model = Service

    def dispatch(self, *args, **kwargs):
        self.bitbucket_username = BITBUCKET_SETTINGS['username']
        self.bitbucket_password = BITBUCKET_SETTINGS['password']
        return super(BitbucketAPIView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            curl = curl_connection(self.bitbucket_username, self.bitbucket_password)
            curl.authenticate()
            post = str()

            if self.request.POST['data'] == 'respositories':
                context = self.repositories(curl)
            elif self.request.POST['data'] == 'addhook':
                context = self.add_hook(curl, request)

            return self.render_json_response(context)

        finally:
            curl.close()

        return HttpResponse()

    def repositories(self, curl):
        """Load list of repositories from bitbucket account"""

        url = 'https://bitbucket.org/api/1.0/user/repositories'
        context = curl.perform(url)
        return context

    def add_hook(self, curl, request):
        """Add hook and change repo_hook flag for service"""

        service = self.get_object()
        url = 'https://api.bitbucket.org/1.0/repositories/%s/%s/services/ ' % (self.bitbucket_username, self.get_object().repo_slug_name)
        post = 'type=POST&URL=%s%s' % (absolute_url(request).build(), service.hook_url())
        service.repo_hook = True
        service.save()
        context = curl.perform_post(url, post)
        return context
