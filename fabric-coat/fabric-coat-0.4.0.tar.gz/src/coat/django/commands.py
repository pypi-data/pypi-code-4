from __future__ import with_statement

import os
import shutil
import glob

from fabric.api import run, local, cd, settings, prefix, hide
from fabric.operations import require
from fabric.state import env
from fabric.contrib import files as fabric_files

from coat import utils as coat_utils
from coat.django.utils import find_settings, find_manage
from coat.django import signals


def copy_revision_to_remote(workdir, remote_revision, deploy_revision):
    # test remote for the revision and skip re-copying already
    # existing revisions
    remote_versions_dir = "%s/%s" % (
        env.base_dir, env.django_settings.versions_dir
    )

    if not fabric_files.exists(remote_versions_dir):
        run("mkdir -p %s" % remote_versions_dir)

    if fabric_files.exists("%s/%s" % (remote_versions_dir,
                                      deploy_revision)):
        return

    # copy all of local onto remote using rsync, use hard links to save
    # space for unmodified files
    rsync_cmd = ("%s/* %s@%%s:%s/%s/" %
                 (workdir, env.user,
                  remote_versions_dir,
                  deploy_revision))

    signals.pre_workdir_copy_to_remote.send(
        sender=copy_revision_to_remote,
        deploy_revision=deploy_revision,
        remote_revision=remote_revision,
        workdir=workdir,
    )

    if remote_revision:
        with cd("%s/%s" % remote_versions_dir):
            run("rsync -a --link-dest=../%(cur)s/ %(cur)s/ %(new)s" %
                {'cur': remote_revision, 'new': deploy_revision})

        rsync_cmd = "-a -c --delete " + rsync_cmd
    else:
        rsync_cmd = "-a " + rsync_cmd

    for host in env.hosts:
        local("rsync %s" % (rsync_cmd % host))

    signals.post_workdir_copy_to_remote.send(
        sender=copy_revision_to_remote,
        deploy_revision=deploy_revision,
        remote_revision=remote_revision,
        workdir=workdir,
    )


def remote_activate_revision(workdir, remote_revision, deploy_revision):
    remote_virtualenv_dir = "%s/%s" % (
        env.base_dir, env.virtualenv_settings.env_dir
    )

    remote_versions_dir = "%s/%s" % (
        env.base_dir, env.django_settings.versions_dir
    )

    signals.pre_remote_run_commands.send(
        sender=remote_activate_revision,
    )

    # initialize virtualenv if non-existant
    if not fabric_files.exists(remote_virtualenv_dir):
        signals.pre_remote_init_virtualenv.send(
            sender=remote_activate_revision
        )

        for command in env.virtualenv_settings.init_commands:
            run(command)

        signals.post_remote_init_virtualenv.send(
            sender=remote_activate_revision
        )

    # find relative path to manage.py
    django_manage_path = find_manage(workdir).replace(workdir, "")[1:]

    with cd("%s/%s" % (remote_versions_dir, deploy_revision)):
        with prefix("source %s/bin/activate" % remote_virtualenv_dir):
            for command in env.virtualenv_settings.commands:
                run(command)

        for command in env.django_settings.management_commands:
            run("%s/bin/python %s %s" % (
                remote_virtualenv_dir, django_manage_path, command
            ))

    signals.post_remote_run_commands.send(
        sender=remote_activate_revision,
    )

    signals.pre_remote_activate_revision.send(
        sender=remote_activate_revision,
    )

    with cd(remote_versions_dir):
        with settings(hide("warnings", "stderr"), warn_only=True):
            run("test -L current && rm current")

        run("ln -s %s current" % deploy_revision)

    signals.post_remote_activate_revision.send(
        sender=remote_activate_revision,
    )


def remote_reload():
    signals.pre_remote_reload.send(sender=remote_reload)

    if env.django_settings.wsgi_file:
        run("touch %s/%s" % (env.base_dir, env.django_settings.wsgi_file))

    signals.post_remote_reload.send(sender=remote_reload)


def workdir_django_prepare(workdir):
    if 'settings_file' in env.django_settings:
        django_basedir = os.path.dirname(find_settings(workdir))

        shutil.copy(
            os.path.join(django_basedir, env.django_settings.settings_file),
            os.path.join(django_basedir, "localsettings.py")
        )

        map(os.unlink, glob.glob("%s/localsettings_*.py" % django_basedir))


def deploy(revision="HEAD"):
    require("django_settings", "base_dir", "virtualenv_settings", provided_by=("env_test", "env_live"))

    env.django_settings.validate_or_abort()
    env.virtualenv_settings.validate_or_abort()

    env.remote_revision = coat_utils.remote_resolve_current_revision()
    env.deploy_revision = coat_utils.local_resolve_revision(revision)

    env.deploy_workdir = coat_utils.workdir_prepare_checkout(
        revision, folders=("django", )
    )

    workdir_django_prepare(env.deploy_workdir)

    copy_revision_to_remote(
        env.deploy_workdir, env.remote_revision, env.deploy_revision
    )

    remote_activate_revision(
        env.deploy_workdir, env.remote_revision, env.deploy_revision
    )

    remote_reload()
