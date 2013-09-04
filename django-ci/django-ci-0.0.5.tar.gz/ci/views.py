
from ci.models import CiProject, CiBranch, TestModule, TestRun, NotificationPref
from ci.tasks import start_test
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
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
import traceback
from django.core.exceptions import ObjectDoesNotExist
import gevent


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

    def get_success_url(self):
        return reverse(self.manager.default_app + ":detail",
            args=[self.object.slug],
            current_app=self.manager.name)


class CiProjectViewSet(BaseViewSet):
    object_url = "(?P<slug>[\w\d\-]+)/"

    def get_success_url(self):
        return reverse(self.manager.default_app + ":detail",
            args=[self.project.slug, self.object.slug],
            current_app=self.manager.name)


class CiBranchViewSet(BaseViewSet):
    base_url = "^ci-projects/(?P<project>[\w\-]+)/branch/"
    object_url = "(?P<slug>[\w\-\d]+)/"

    def get_queryset(self, view, request, **kwargs):
        view.project = get_object_or_404(CiProject, slug=kwargs.get("project"))
        retval = CiBranch.objects.filter(project=view.project)
        return retval


class NotificationViewSet(BaseViewSet):

    def get_queryset(self, view, request, **kwargs):
        if request.user.is_authenticated():
            return NotificationPref.objects.filter(user=request.user)
        else:
            return NotificationPref.objects.none()


ciprojects = CiProjectViewSet(model=CiProject, template_dir="ci/ci-projects")
cibranches = CiBranchViewSet(model=CiBranch, template_dir="ci/ci-branches")
notifications = NotificationViewSet(model=NotificationPref, template_dir="ci/notifications")


@ciprojects.instance_view("hook")
class HookDetailView(ViewSetMixin, DetailView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return DetailView.dispatch(self, request, *args, **kwargs)

    def post(self, request, slug):
        try:
            package = json.loads(request.body)
            name = package['repository']['name']
            branch = package['ref'].rsplit("/")[-1]
            if name and branch:
                project = CiProject.objects.get_or_create(
                    name=name,
                    url=package['repository']['url']
                )[0]

                # check if branch was deleted
                after = package.get("after")
                commits = package.get("total_commits_count")

                if commits == 0 and len(after.replace("0", "")) == 0:

                    # branch was deleted
                    try:
                        branch = CiBranch.objects.get(
                            project=project,
                            name=branch
                        )
                        branch.delete()
                    except ObjectDoesNotExist:
                        pass
                else:
                    branch = CiBranch.objects.get_or_create(
                        project=project,
                        name=branch
                    )[0]

                    gevent.spawn_later(2, branch.test)
        except:
            traceback.print_exc()

        return HttpResponse("OK")


@cibranches.instance_view("test")
class TestDetailView(ViewSetMixin, DetailView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return DetailView.dispatch(self, request, *args, **kwargs)

    def post(self, request, project, slug):
        self.object = self.get_object()

        if self.object.celery_id:
            result = AsyncResult(self.object.celery_id)
            result.revoke(terminate=True)

        gevent.spawn_later(2, self.object.test)

        messages.info(request, "test queued")

        return redirect(request.META.get("HTTP_REFERER",
            reverse_lazy("ci-projects:detail", args=[self.object.pk])))


@cibranches.instance_view("pull")
class PullProjectView(ViewSetMixin, SingleObjectMixin, View):

    def post(self, request, project, slug):
        self.object = self.get_object()
        gevent.spawn_later(2, self.object.setup_venv)
        messages.success(request, "Queued Pull")
        return redirect(request.META.get("HTTP_REFERER",
            reverse_lazy("ci-projects:detail", args=[self.object.pk])))


@cibranches.instance_view("start")
class StartServerView(ViewSetMixin, SingleObjectMixin, View):

    def post(self, request, project, slug):
        self.object = self.get_object()
        server = self.object.get_server()
        if not server:
            server = self.object._create_server()
            if not server:
                messages.error(request, "Sorry, couldn't create server")
        return redirect(request.META.get("HTTP_REFERER",
            reverse_lazy("ci-projects:detail", args=[self.object.pk])))


@cibranches.instance_view("stop")
class StopServerView(ViewSetMixin, SingleObjectMixin, View):

    def post(self, request, project, slug):
        self.object = self.get_object()
        self.object._stop_server()
        messages.success(request, "Server stopped")
        return redirect(request.META.get("HTTP_REFERER",
            reverse_lazy("ci-projects:detail", args=[self.object.pk])))
