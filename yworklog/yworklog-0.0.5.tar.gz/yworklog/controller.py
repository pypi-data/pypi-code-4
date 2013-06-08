#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
from cement.core import foundation, controller, handler
from .model import WorkLog, StartAttrs
from datetime import datetime
from . import fsm
import os
import os.path
from os.path import dirname,realpath,abspath,join
from shutil import copyfile
import stat

#log = logging.getLogger(__name__)

class WorkLogController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = 'WorkLog entry point'

class ActivityWriter(controller.CementBaseController):
    def _activity(self):
        wl = WorkLog()
        wl.activity = self._meta.label
        wl.description = " ".join(self.pargs.args)
        self.app.session.add(wl)
        self.app.session.commit()
        return wl

class StartController(ActivityWriter):
    class Meta:
        interface = controller.IController
        label = 'start'
        description = 'start an activity'
        arguments = [
            (['-p', '--project'], dict(type=str, help='project name, used for matching git repository') ),
            (['-r', '--reference'], dict(type=int, help='issue reference number, used for prepare-commit-msg hook')),
            (['args'], dict(metavar='activity', type=str, nargs='*', help='activity name/description')),
        ]
        aliases= ['s']

    def validate_args(self):
        err = False
        if not self.pargs.project and not self.pargs.reference:
            if self.pargs.args == []:
                err = True
        elif bool(self.pargs.project) ^ bool(self.pargs.reference):
            err = True
        else:
            self.pargs.args.insert(0, "project: %s; ref: %s" % (self.pargs.project, self.pargs.reference))
        if err:
            raise RuntimeError("there must be args or both project and reference specified")

    def _start_attrs(self):
        if not self.pargs.project:
            return

        sa = StartAttrs()
        sa.project = self.pargs.project
        sa.ref = self.pargs.reference
        self.wl.start_attrs = sa
        self.app.session.add(sa)
        self.app.session.commit()

    @controller.expose()
    def default(self):
        self.validate_args()
        self.wl = self._activity()
        self._start_attrs()

class EndController(ActivityWriter):
    class Meta:
        interface = controller.IController
        label = 'end'
        description = 'end last activity'
        arguments = [(['args'], dict(type=str, nargs='*', metavar='description'))]
        aliases=['e']

    @controller.expose()
    def default(self):
        self._activity()


class ResumeController(ActivityWriter):
    class Meta:
        interface = controller.IController
        label = 'resume'
        description = 'resume last activity'
        arguments = [(['args'], dict(type=str, nargs='*', metavar='description'))]
        aliases=['r']

    @controller.expose()
    def default(self):
        self._activity()

def display(items):
    [print(unicode(i)) for i in items]

def display_diff(items, diff):
    display(items)
    print("diff: %s" % diff)

class ListController(controller.CementBaseController):
    class Meta:
        interface = controller.IController
        label = 'list'
        description = 'list log'
        arguments = []
        aliases=['l']

    @controller.expose()
    def default(self):
        display(self.app.session.query(WorkLog).all())

class DiffController(controller.CementBaseController):
    class Meta:
        interface = controller.IController
        label = 'diff'
        description = 'diff now() since last log'
        arguments = [(['-f', '--full'], dict(action='store_true'))]
        aliases=['d']

    @controller.expose()
    def default(self):
        self.log.debug(self.pargs)
        if self.pargs.full:
            items, state = WorkLog.iterate(fsm.DiffGetter(), self.app.session)
            diff = state[2]
        else:
            wl = self.app.session.query(WorkLog).order_by(WorkLog.created_at.desc()).limit(1).one()
            diff = datetime.now() - wl.created_at
            items = [wl]

        display_diff(items, diff)

class PopController(controller.CementBaseController):
    class Meta:
        interface = controller.IController
        label = 'pop'
        description = 'diff now() since last log'
        arguments = []
        aliases=['p']

    @controller.expose()
    def default(self):
        items, state = WorkLog.iterate(fsm.DiffGetter(), self.app.session)
        display_diff(items, state[2])
        [self.app.session.delete(i) for i in items]
        self.app.session.commit()

class GetRefController(controller.CementBaseController):
    class Meta:
        interface = controller.IController
        label = 'getref'
        description = 'get ref'
        arguments = [(['-p', '--project'], dict(type=str, required=True))]

    @controller.expose()
    def default(self):
        item = WorkLog.iterate(fsm.StartGetter(), self.app.session)
        sa = item.start_attrs
        if not sa:
            exit(1)

        if not sa.project == self.pargs.project:
            exit(1)

        print(sa.ref)

class FlushController(controller.CementBaseController):
    class Meta:
        interface = controller.IController
        label = 'flush'
        description = 'flush'
        arguments = []

    @controller.expose()
    def default(self):
        for i in self.app.session.query(WorkLog).all(): self.app.session.delete(i)
        self.app.session.commit()

class GitHookInstallController(controller.CementBaseController):
    class Meta:
        interface = controller.IController
        label = 'githookinstall'
        description = 'githookinstall, assumes calling from git root dir'
        arguments = [(['-p', '--project'], dict(type=str, required=True))]

    @controller.expose()
    def default(self):
        hook_dir = join(os.getcwd(), ".git", "hooks")
        if not os.path.isdir(hook_dir):
            raise RuntimeError("I don't recognize this as a git root dir")

        hook = join(hook_dir, "prepare-commit-msg")

        if not os.path.isfile(hook):
            copyfile(hook + ".sample", hook)
            os.chmod(hook, stat.S_IXUSR | stat.S_IWUSR | stat.S_IRUSR)

        git_hooks_dir = join(dirname(abspath(realpath(__file__))), "git-hooks")
        hook_call = "sh %s %s $@\n" % (
            os.path.join(git_hooks_dir,"prepare-commit-msg"),
            self.pargs.project)

        f = open(hook, "a")
        f.write(hook_call)
        f.close()

export = [StartController, EndController, ResumeController, ListController,
DiffController, PopController, GetRefController, FlushController,
GitHookInstallController]
