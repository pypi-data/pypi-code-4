from celery.result import AsyncResult
from ci.virtualenvapi.manage import VirtualEnvironment
from django.core.management import call_command
from django.db import models
from django.db.models import Q
from django.db.models.aggregates import Count
from django.template.defaultfilters import slugify
from socketio_server.options import emit_to_all
from os import path
import datetime
import git
import os
import re
import shlex
import signal
import subprocess
import traceback
import gevent
from subprocess import Popen
from django.core.mail import send_mail
from git.exc import GitCommandError


class Server:
    ports = range(8003, 8011)
    available_ports = ports[:]
    servers = {}


NOTIFICATIONS = (
    ("test_started", "A test suite has started"),
    ("test_ended", "A test suite has finished"),
    ("test_failures", "A test suite reported failures"),
    ("test_success", "A test suite reported 100% success"),
)


class NotificationPrefManager(models.Manager):
    pass


def fetch_attrib(name):
    def inner(self):
        return self.get_query_set().get(notification=name)
    return inner

for name, desc in NOTIFICATIONS:
    setattr(NotificationPrefManager, name, fetch_attrib(name))


class NotificationPref(models.Model):
    user = models.ForeignKey("auth.User", related_name="notifications")
    notification = models.CharField(max_length=30, choices=NOTIFICATIONS)
    email = models.BooleanField(blank=True)
    html = models.BooleanField(blank=True)

    objects = NotificationPrefManager()


class CommandGroup(models.Model):
    project = models.ForeignKey("CiProject")
    branch = models.CharField(blank=True, max_length=255,
        help_text="leave blank to apply to all branches")
    type = models.CharField(max_length=50,
        choices=(("test", "Test Commands"), ("server", "Commands to run server"))
    )


class Command(models.Model):
    class Meta:
        ordering = ("ordering",)
    project = models.ForeignKey("CommandGroup")
    ordering = models.SmallIntegerField(default=100)
    working_directory = models.CharField(max_length=255,
        help_text="relative to the environment")
    commands = models.TextField(help_text="One command per line")
    environment = models.TextField(blank=True,
        help_text="One environment variable per line: DJANG_SETTINGS_MODULE=superior.settings")

    @property
    def env(self):
        data = {}
        for line in self.environment.split("\n"):
            name, value = line.split("=", 1)
            data[name] = value
        return data


class CiProject(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, blank=True)
    url = models.CharField(max_length=255)
    dependancies = models.TextField(blank=True,
        help_text="pip modules (django==1.4) or "
                  "git references (install [folders,...] from [git])")
    manage_location = models.CharField(max_length=255, blank=True,
        help_text="Where the manage.py command is for django projects")
    settings_module = models.CharField(max_length=255, blank=True,
        help_text="Django settings module")

    def __unicode__(self):
        return u"%s" % (self.name)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(CiProject, self).save(**kwargs)


class CiBranch(models.Model):
    class Meta:
        unique_together = ("project", "name")
        verbose_name_plural = "Ci-Branches"
    project = models.ForeignKey(CiProject, related_name="branches")
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    dependancies = models.TextField(blank=True,
        help_text="Additional dependancies")
    celery_id = models.CharField(max_length=50, editable=False,)

    def __unicode__(self):
        return u"%s@%s" % (self.project.name, self.name)

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(CiBranch, self).save(**kwargs)

    @property
    def git_head(self):
        try:
            repo = git.Repo(path.join(self.path, self.repo_path))
            return repo.head.commit
        except:
            return None

    @property
    def testing_status(self):
        if self.celery_id:
            try:
                result = AsyncResult(self.celery_id)
                return result.state
            except:
                traceback.print_exc()
        return ""

    @property
    def path(self):
        name = "%s@%s" % (self.project.slug, self.slug)
        path = 'builds/%s/' % name
        return path

    def get_repo_path(self, url):
        return os.path.basename(url).rsplit(".", 1)[0]

    @property
    def repo_path(self):
        return self.get_repo_path(self.project.url)

    def resolve_dependancies(self, env, dependancies):
        for dependancy in dependancies:
            groups = re.match("install ([a-z_\-\d/, ]+) from (.+)$", dependancy)
            if groups:
                modules = groups.group(1).split(",")
                location, refid = groups.group(2).rsplit("@", 1)

                # is there a branch?
                if ".git" not in location:
                    location = location + "@" + refid
                    refid = "master"
                else:
                    refid = refid.strip()

                my_path = os.path.join(self.path, self.get_repo_path(location))

                if os.path.exists(my_path):
                    repo = git.Repo(my_path)
                    created = False
                else:
                    repo = git.Repo.clone_from(location, my_path)
                    repo.clone(location)
                    created = True

                repo.git.checkout(refid)
                repo.head.reset(index=True, working_tree=True)
                if not created:
                    self._test_update("pulling: %s" % location)
                    repo.git.pull()

                # move to local
                for module in modules:
                    module = module.strip()
                    if module == "all":
                        module = os.path.basename(location).split(".")[0]
                        modules = []
                    else:
                        modules = [module]
                        module = module.split("/")[-1]

                    if os.name == "nt":
                        args = [
                            "mklink", "/J",
                            '"%s"' % os.path.join(self.path, "Lib", "site-packages", module),
                            '"%s"' % os.path.join(my_path, *modules)
                        ]
                    else:
                        args = [
                            "ln", "-s",
                            '"%s"' % os.path.abspath(os.path.join(my_path, *modules)),
                            '"%s"' % os.path.join(self.path, "lib", "python2.7", "site-packages", module),
                        ]
                    try:
                        cmd = " ".join(args)
                        self._test_update("linking: %s" % cmd)
                        os.system(cmd)
                    except:
                        pass  # already exists?
            else:
                args = [
                    "pip", "install", "-q", "--upgrade", dependancy
                ]
                env._execute(args)
                cmd = " ".join(args)
                self._test_update("pipping: %s" % cmd)

            # take a break
            gevent.sleep(0)

    def setup_venv(self):
        path = self.path
        try:
            os.makedirs(path)
        except:
            pass

        print "setting up environment: %s" % path
        env = VirtualEnvironment(path)
        env.open_or_create()

        self.pull(env)

        if self.project.dependancies:
            print "resolving project dependancies"
            self.resolve_dependancies(env, self.project.dependancies.split("\n"))

        if self.dependancies:
            print "resolving branch dependancies"
            self.resolve_dependancies(env, self.dependancies.split("\n"))

        requirements_file = os.path.join(env.path, self.repo_path, "requirements.txt")
        if os.path.exists(requirements_file):
            print "resolving requirements.txt dependancies"
            with open(requirements_file) as fileh:
                self.resolve_dependancies(env, fileh)

        return env

    def pull(self, env=None, path=None):
        if not path:
            path = self.path

        my_path = os.path.join(path, self.repo_path)

        if os.path.exists(my_path):
            repo = git.Repo(my_path)
            created = False
        else:
            repo = git.Repo.clone_from(self.project.url, my_path)
            repo.clone(self.project.url)
            created = True

        repo.git.checkout(self.name)
        repo.head.reset(index=True, working_tree=True)
        if not created:
            try:
                print repo.git.pull()
            except:
                print "ERROR"
                traceback.print_exc()
                print

    def _test_update(self, message):
        packet = dict(
            name=self.project.name,
            branch=self.name,
            message=message
        )
        emit_to_all("test_progress", packet)

    def test(self):
        try:
            self._test_update("Test Started")

            self._test_update("Clearing previous Test Results")
            self.testrun_set.all().delete()

            self._test_update("Setting Up Virtual Environment")
            env = self.setup_venv()

            environment = os.environ.copy()
            groups = CommandGroup.objects.filter(
                Q(branch=self.name) | Q(branch=""),
                project=self.project,
                type="test",
            ).order_by("branch")

            if len(groups) > 0:
                group = groups[0]
                for command in group.command_set.all():
                    my_environment = environment.copy()
                    my_environment.update(command.env)

                    for line in command.commands.split("\n"):
                        cmds = shlex.split(line)
                        if cmds:
                            self._test_update("Running: `%s`" % ' '.join(cmds))
                            env._execute(cmds,
                                cwd=command.working_directory, env=my_environment)

            self._test_update("Getting results")
            call_command("import_testresults", self.project.name, self.name,
                os.path.join(env.path, self.repo_path, "superiordjango", "testresults.json"))

            self._test_update("Done")
        except Exception, ex:
            print type(ex), dir(ex)

            if isinstance(ex, GitCommandError):
                error = "Error running git command: %s" % (
                    [ex.command, ex.args, ex.status, ex.stderr],)
            else:
                error = "%s" % ex

            self._test_update("Exception! %s" % error)
            TestRun.objects.create(
                branch=self,
                module=TestModule.objects.get_or_create(name="ci")[0],
                name="Setting up Test",
                status="fail",
                description=error,
                error=traceback.format_exc()
            )

        if self.stats().filter(status="fail").count() > 0:
            emails = NotificationPref.objects.filter(
                notification="test_failures",
                email=True
            ).values_list("user__email", flat=True)

            if emails:
                send_mail("Test Failures", "%s %s" % (self.project.name, self.name),
                    from_email="ci-server@leithall.com",
                    recipient_list=emails)
        else:
            emails = NotificationPref.objects.filter(
                notification="test_success",
                email=True
            ).values_list("user__email", flat=True)

            if emails:
                send_mail("Test Success", "%s %s" % (self.project.name, self.name),
                    from_email="ci-server@leithall.com",
                    recipient_list=emails)

    def stats(self):
        return self.testrun_set.values("status").annotate(count=Count("status"))

    def _create_server(self):
        groups = CommandGroup.objects.filter(
            Q(branch=self.name) | Q(branch=""),
            project=self.project,
            type="server"
        ).order_by("branch")

        if len(groups) and len(Server.available_ports) > 0:
            group = groups[0]
            env = self.setup_venv()

            port = Server.available_ports[0]
            Server.available_ports = Server.available_ports[1:]
            server = None
            for command in group.command_set.all():
                for line in command.commands.split("\n"):
                    cmds = shlex.split(line)
                    for i, cmd in enumerate(cmds):
                        if cmd == ":interface:":
                            cmds[i] = "0.0.0.0:%s" % port
                    if cmds:
                        server = env._execute(cmds,
                            cwd=command.working_directory, env=command.env,
                            return_process=True)

            if server:
                Server.servers[self] = {"port": port, "process": server}
            else:
                print "failed to start server"
        return self.get_server()

    def _stop_server(self):
        server = Server.servers.get(self)
        if server:

            server['process'].send_signal(signal.SIGINT)
            os.killpg(server['process'].pid, signal.SIGKILL)

            Server.available_ports.append(server['port'])
            del Server.servers[self]

    def get_server(self):
        if self in Server.servers:
            server = Server.servers.get(self)
            if not server['process'].poll() is None:
                Server.available_ports.append(server['port'])
                del Server.servers[self]

        return Server.servers.get(self)

    def get_server_url(self, request):
        server = self.server()
        if server:
            return "http://%s:%s" % (request.get_host(), server[0])

    @property
    def last_run(self):
        return self.testrun_set.latest("created_at")


class TestModule(models.Model):
    class Meta:
        ordering = ("name",)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class TestRunManager(models.Manager):

    def failures(self):
        return self.get_query_set().filter(status__in=("fail", "error", "unexpected success"))

    def successes(self):
        return self.get_query_set().exclude(status__in=("fail", "error", "unexpected success"))


class TestRun(models.Model):
    class Meta:
        ordering = ("module", "name",)
    created_at = models.DateTimeField(auto_now=True)
    branch = models.ForeignKey(CiBranch)
    module = models.ForeignKey(TestModule)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)

    objects = TestRunManager()

    def __unicode__(self):
        return self.name

    def label(self):
        return {
            "success": "success",
            "skip": "default",
            "fail": "important",
            "error": "important",
            "expected failure": "success",
            "unexpected success": "important",
        }.get(self.status, "important")
