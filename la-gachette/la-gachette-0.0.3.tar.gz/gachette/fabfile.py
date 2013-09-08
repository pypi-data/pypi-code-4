#!/usr/bin/env python
#code: utf-8

import os
import shutil
import fabric.main
from fabric.api import task, env
from fabric.main import load_settings
from fabric.utils import abort, puts

from gachette.working_copy import WorkingCopy
from gachette.stack import Stack
from gachette import get_version

"""
Usage for a simple application repo. First we create the stack in a certain location:

    fab -H vagrant@0.0.0.0 stack_create:foobar1,/var/gachette

From now on, you can add as many as packages as you want for this stack.
We clone the repository and checkout a specific branch:

    fab -H vagrant@0.0.0.0 prepare:test_config_first_build,git@github.com:ops-config/test_config

Now we build the packages (note: the name is use as a key). Location where the packages should end up is specify:

    fab -H vagrant@0.0.0.0 build:test_config_first_build,/var/gachette/debs

Now adding a package to the stack. We need to specify the package information as they came from the last command:

    fab -H vagrant@0.0.0.0 add_to_stack:dh-secret-sauce-live,1.0.0,dh-secret-sauce-live-1.0.0-all.deb,/var/gachette,foobar1

"""

# allow the usage of ssh config file by fabric
env.use_ssh_config = True

# load the rc file (needed hack: https://github.com/fabric/fabric/pull/586)
env.rcfile = os.path.expanduser("~/.gachetterc")
settings = load_settings(env.rcfile)
if settings:
    env.update(settings)
    if 'build_host' in env:
        env.hosts = [env.build_host]

@task
def init_config():
    """
    Create the .gachetterc if not there.
    """
    if os.path.exists(env.rcfile):
        abort("""You already have a %s config file.
        Before creating a new version (with maybe udpated comments), you should back it up and remove it.""" % env.rcfile)

    shutil.copy("gachette/templates/gachetterc.txt", env.rcfile)
    puts("""Congrats! you now have a configuration file available for you to edit!
        Just open %s and follow the instruction.""" % env.rcfile)

@task
def version():
    print get_version()


@task
def stack_create(name, target_folder, from_stack=None):
    """
    Create a new stack. From old one if specified.
    """
    new_stack = Stack(name, target_folder=target_folder)

    if not new_stack.is_persisted():
        if from_stack:
            old_stack = Stack(from_stack)
            new_stack.clone_from(old_stack)
        else:
            new_stack.persist()


@task
def prepare(name, url=None, branch='master'):
    """
    Prepare the working copy remotely for the project.
    <name> of the working copy folder.
    <url> is the url of the repo in github.
    <branch> is the branch to actually checkout.
    """
    wc = WorkingCopy(name)
    wc.prepare_environment()
    return wc.checkout_working_copy(url, branch)


@task
def build(name,
          output_path,
          path_to_missile=None,
          app_version=None,
          env_version=None,
          service_version=None,
          webcallback=None):
    """
    Build the package for the working copy remotely via trebuchet.
    <name> of the working copy folder.
    <output_path> path to where the DEB package should be created into.
    <path_to_missile> relative path to the missile file for trebuchet
    <app_version> version specific for the application package built.
    <env_version> version specific for the lib/environment package built.
    <service_version> version specific for the services packages built.
    <webcallback> web URI to send Trebuchet callbacks to.
    """
    wc = WorkingCopy(name)
    wc.set_version(app=app_version, env=env_version, service=service_version)
    wc.build(output_path, path_to_missile, webcallback)


@task
def add_to_stack(name, version, file_name, target_folder, stack_version=None):
    """
    Add created package to stack and reference packages.
    <name> actual name of the package.
    <version> version of the package.
    <file_name> exact file_name of the package (versioned, architecture...).
    <target_folder> path to the stacks
    <stack_version> version of the stack to attach the package to.
    """
    stack = Stack(stack_version, target_folder=target_folder)
    stack.add_package(name, version, file_name)


@task
def show_config():
    """
    Dummp settings.
    """
    for key in sorted(env.iterkeys()):
        print "%s: %s" % (key, env[key])


def main():
    """
    Allow the execution of the fabfile in standalone.
    even as entry_point after installation via setup.py.
    """
    # locate the fabfile
    current_file = os.path.abspath(__file__)
    if current_file[-1] == "c":
        current_file = current_file[:-1]

    # launch fabric main function
    fabric.main.main([current_file])


if __name__ == '__main__':
    main()
