from ci.models import CiProject
from ci.tasks import start_test
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.views.generic.detail import DetailView, SingleObjectMixin
from pprint import pprint
import json
import subprocess
from viewsets import ViewSet, ViewSetMixin
from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


class BaseViewSet(ViewSet):    

    def protect(self, function):
        if not hasattr(function, "protected"):
            def inner(self, request, *args, **kwargs):
#                 if not request.user.is_authenticated():
#                     return redirect("%s?next=%s" % (settings.LOGIN_URL, request.path))
                return function(self, request, *args, **kwargs)
            inner.protected = True
            return inner
        return function

ci_viewset = BaseViewSet(model=CiProject, template_dir="ci/ci-projects")


@ci_viewset.instance_view("test")
class TestDetailView(ViewSetMixin, DetailView):
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return DetailView.dispatch(self, request, *args, **kwargs)
    dispatch.csrf_exempt = True

    def post(self, request, pk):
        self.object = self.get_object()
        
        if self.object.celery_id:
            result = AsyncResult(self.object.celery_id)
            result.revoke(terminate=True)

        result = start_test.apply_async([self.object.name, self.object.branch])
        self.object.celery_id = result.task_id
        self.object.save()

        messages.info(request, "test queued")

        return redirect(request.META.get("HTTP_REFERER",
            reverse_lazy("ci-projects:detail", args=[self.object.pk])))


@ci_viewset.instance_view("pull")
class PullProjectView(ViewSetMixin, SingleObjectMixin, View):

    def post(self, request, pk):
        self.object = self.get_object()
        self.object.pull(None)
        messages.success(request, "Pulled")
        return redirect(request.META.get("HTTP_REFERER",
            reverse_lazy("ci-projects:detail", args=[self.object.pk])))


@ci_viewset.instance_view("start")
class StartServerView(ViewSetMixin, SingleObjectMixin, View):

    def post(self, request, pk):
        self.object = self.get_object()
        server = self.object.get_server()
        if not server:
            server = self.object._create_server()
            if not server:
                messages.error(request, "Sorry, couldn't create server")
        return redirect(request.META.get("HTTP_REFERER",
            reverse_lazy("ci-projects:detail", args=[self.object.pk])))


@ci_viewset.instance_view("stop")
class StopServerView(ViewSetMixin, SingleObjectMixin, View):

    def post(self, request, pk):
        self.object = self.get_object()
        self.object._stop_server()
        messages.success(request, "Server stopped")
        return redirect(request.META.get("HTTP_REFERER",
            reverse_lazy("ci-projects:detail", args=[self.object.pk])))


class TriggerTest(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TriggerTest, self).dispatch(request, *args, **kwargs)

    def get(self, request, name, branch):
        print request.GET

        return HttpResponse("OK")

    def post(self, request, name, branch):
        pprint(json.loads(request.body))

        process = subprocess.Popen(["python", "manage.py", "citests", name, branch])
        print process.communicate()

        return HttpResponse("OK")
