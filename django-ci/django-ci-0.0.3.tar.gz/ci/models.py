from ci.virtualenvapi.manage import VirtualEnvironment
from django.core.management import call_command
from django.db import models
from django.db.models.aggregates import Count
from django.template.defaultfilters import slugify
from os import path
import datetime
import os
import re
import shlex
import signal
import subprocess
import traceback
import git
from celery.result import AsyncResult


class Server:
    ports = range(8003, 8011)
    available_ports = ports[:]
    servers = {}


class CiProject(models.Model):
    class Meta:
        unique_together = ("name", "branch")
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=255)
    branch = models.CharField(max_length=50)
    manage_location = models.CharField(max_length=255, blank=True, null=True)
    settings_location = models.CharField(max_length=255, blank=True, null=True)
    test_commands = models.TextField(null=True, blank=True)
    dependancies = models.ManyToManyField("self", blank=True)
    celery_id = models.CharField(max_length=50)

    def __unicode__(self):
        return u"%s@%s" % (self.name, self.branch)

    @property
    def git_head(self):
        repo = git.Repo(path.join(self.path, self.repo_path))
        return repo.head.commit

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
        name = "%s@%s" % (slugify(self.name), slugify(self.branch))
        path = 'builds/%s/' % name
        return path

    def get_repo_path(self, url):
        return os.path.basename(url).rsplit(".", 1)[0]

    @property
    def repo_path(self):
        return self.get_repo_path(self.url)
    
    def setup_venv(self):
        path = self.path
        try:
            os.makedirs(path)
        except:
            pass

        print "setting up environment: %s" % path
        env = VirtualEnvironment(path)

        self.pull(env)

        if self.dependancies.exists():
            print "pulling dependancies"
            for dependancy in self.dependancies.all():
                print dependancy
                dependancy.pull(env, self.path)

        requirements_file = os.path.join(env.path, self.repo_path, "requirements.txt")
        if os.path.exists(requirements_file):
            print "setting up requirements"
            with open(requirements_file) as fileh:
                for dependancy in fileh:
                    print dependancy
                    groups = re.match("install ([a-z_\-\d, ]+) from (.+)$", dependancy)
                    if groups:
                        modules = groups.group(1).split(",")
                        location, refid = groups.group(2).rsplit("@", 1)

                        # is there a branch?
                        if ":" not in location:
                            location = location + refid
                            refid = "master"

                        print modules, location, refid

                        dependancy = CiProject(
                            url=location,
                            branch=refid
                        )
                        dependancy.pull(env, self.path)

                        for module in modules:
                            module = module.strip()
                            print module
                            args = [
                                "mklink", "/J",
                                '"%s"' % os.path.join(self.path, "Lib", "site-packages", module),
                                '"%s"' % os.path.join(self.path, dependancy.repo_path, module)
                            ]
                            print " ".join(args)
                            if os.name == "nt":
                                os.system(" ".join(args))
#                                 env._execute(args)
                            else:
                                pass  # not sure right now.
                    else:
                        if os.name == "nt":
                            env._execute([
                                "Scripts/pip", "install", "-q", "--upgrade",
                                dependancy
                            ])
                        else:
                            env._execute([
                                "bin/pip", "install", "-q", "-r",
                                dependancy
                            ])

        return env

    def pull(self, env=None, path=None):
        if not path:
            path = self.path

        print "pulling", self.url, "to", path
        my_path = os.path.join(path, self.repo_path)

        if os.path.exists(my_path):
            repo = git.Repo(my_path)
            created = False
        else:
            repo = git.Repo.clone_from(self.url, my_path)
            print "clone:", repo.clone(self.url)
            created = True

        print repo.git.config(l=True)
        print "checkout:", getattr(repo.heads, self.branch).checkout()
        print "reset:", repo.head.reset(index=True, working_tree=True)
        if not created:
            try:
                print repo.git.pull()
            except:
                print "ERROR"
                traceback.print_exc()
                print

    def test(self):

        env = self.setup_venv()
        envc = os.environ.copy()
        if os.name == "nt":
            envc["PATH"] = str(os.path.abspath(os.path.join(env.path, "Scripts")) + ":" + envc.get("PATH", ""))
        else:
            envc["PATH"] = str(os.path.abspath(os.path.join(env.path, "bin")) + ";" + envc.get("PATH", ""))
        envc["DJANGO_SETTINGS_MODULE"] = str(self.settings_location)
        print envc

        for command in self.test_commands.split("\n"):
            if ";;;" in command:
                command, cwd = command.split(";;;", 1)
            else:
                cwd = None
            cmds = shlex.split(command)
            if cmds:
                env._execute(cmds, cwd=cwd, env=envc)

        call_command("import_testresults", self.name, self.branch,
            os.path.join(env.path, self.repo_path, "superiordjango", "testresults.json"))

    def stats(self):
        return self.testrun_set.values("status").annotate(count=Count("status"))

    def _create_server(self):
        if len(Server.available_ports) > 0:
            port = Server.available_ports[0]
            Server.available_ports = Server.available_ports[1:]
            
            env = self.setup_venv()
            args = ["python", "manage.py", "runserver", "0.0.0.0:%s" % port]
            cwd = os.path.join(env.path, os.path.dirname(self.manage_location))
            envc = os.environ.copy()
            envc["PATH"] = str(os.path.abspath(os.path.join(env.path, "Scripts")) + ":" + envc.get("PATH", ""))
            envc["PYTHONPATH"] = ".;%s" % self.repo_path
            envc["DJANGO_SETTINGS_MODULE"] = str(self.settings_location)
            print envc
            server = subprocess.Popen(args, env=envc, cwd=cwd,
                preexec_fn=os.setsid)
            Server.servers[self] = {"port": port, "process": server}
        return self.get_server()

    def _stop_server(self):
        server = Server.servers.get(self)
        if server:

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
    project = models.ForeignKey(CiProject)
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
        
