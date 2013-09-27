#!/usr/bin/env python
#code: utf-8

import os
import fabric.main
from fabric.api import task, env
from fabric.utils import abort, puts

from lib.working_copy import WorkingCopy
from lib.stack import Stack
from lib import get_version
from lib.utils import get_config

"""
Usage for a simple application repo. First we create the stack in a certain location:

    fab -c vagrant@0.0.0.0 stack_create:main,foobar1,/var/gachette

From now on, you can add as many as packages as you want for this stack.
We clone the repository and checkout a specific branch:

    fab -H vagrant@0.0.0.0 prepare:test_config_first_build,git@github.com:ops-config/test_config

Now we build the packages (note: the name is use as a key). Location where the packages should end up is specify:

    fab -H vagrant@0.0.0.0 build:test_config_first_build,/var/gachette/debs

Now adding a package to the stack. We need to specify the package information as they came from the last command:

    fab -H vagrant@0.0.0.0 add_to_stack:main,dh-secret-sauce-live,1.0.0,dh-secret-sauce-live-1.0.0-all.deb,/var/gachette,foobar1

"""

# monkey patch this to load yaml
fabric.main.load_settings = get_config

# allow the usage of ssh config file by fabric
env.use_ssh_config = True
env.forward_agent = True


@task
def version():
    print get_version()


@task
def stack_create(domain, name, meta_path=None, from_stack=None):
    """
    Create a new stack. From old one if specified.
    """
    # get the meta_path from .gachetterc
    meta_path = meta_path if 'meta_path' not in env else env.meta_path
    if not meta_path:
        abort("Please specify a `meta_path` or use a config file to define it")
    
    new_stack = Stack(domain, name, meta_path=meta_path)

    if not new_stack.is_persisted():
        if from_stack:
            old_stack = Stack(domain, from_stack, meta_path=meta_path)
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
          debs_path=None,
          path_to_missile=None,
          app_version=None,
          env_version=None,
          service_version=None,
          webcallback=None):
    """
    Build the package for the working copy remotely via trebuchet.
    <name> of the working copy folder.
    <debs_path> path to where the DEB package should be created into.
    <path_to_missile> relative path to the missile file for trebuchet
    <app_version> version specific for the application package built.
    <env_version> version specific for the lib/environment package built.
    <service_version> version specific for the services packages built.
    <webcallback> web URI to send Trebuchet callbacks to.
    """
    # Get value from .gachetterc
    debs_path = debs_path if 'debs_path' not in env else env.debs_path
    if debs_path is None:
        abort("""
            Either specify the debs_path in your call or add it to the .gachetterc file.""")

    wc = WorkingCopy(name)
    wc.set_version(app=app_version, env=env_version, service=service_version)
    wc.build(debs_path, path_to_missile, webcallback)


@task
def add_to_stack(domain, name, version, file_name, meta_path, stack_version):
    """
    Add created package to stack and reference packages.
    <name> actual name of the package.
    <version> version of the package.
    <file_name> exact file_name of the package (versioned, architecture...).
    <meta_path> path to the stacks and other meta information related to package
    <stack_version> version of the stack to attach the package to.
    """
    # get the meta_path from .gachetterc
    meta_path = meta_path if 'meta_path' not in env else env.meta_path
    
    stack = Stack(domain, stack_version, meta_path=meta_path)
    stack.add_package(name, version, file_name)


@task
def show_config():
    """
    Dummp settings.
    """
    for key in sorted(env.iterkeys()):
        print "%s: %s" % (key, env[key])


@task
def quick(domain, stack_version, project_name, branch="master", url=None, path_to_missile=None, debs_path=None, meta_path=None):
    """
    One-command to build and add to stack a specific branch.
    Depends heavily on pre-configuration via config file.
    Package version are set from Git commit.

    <domain> domain where the stack will be registered to (some kind of type for stack).
    <stack_version> version of the stack to attach the package to.
    <project_name> name of the project.
    <branch> is the branch to actually checkout.
    <url> is the url of the repo in github.
    <path_to_missile> is the path to the missile file in the project that will be used by trebuchet to build packages.
    <debs_path> path to where the DEB package should be created into.
    <meta_path> path to the stacks and other meta information related to package
    """
    # Get value for the project, complain otherwise
    meta_path = meta_path if 'meta_path' not in env else env.meta_path
    debs_path = debs_path if 'debs_path' not in env else env.debs_path
    url = url if "projects" not in env or project_name not in env.projects or 'url' not in env.projects[project_name] else env.projects[project_name]['url']
    path_to_missile = path_to_missile if "projects" not in env or project_name not in env.projects or 'path_to_missile' not in env.projects[project_name] else env.projects[project_name]['path_to_missile']
    
    if not meta_path or not debs_path:
        abort("Please specify a meta_path/debs_path or add it approprietly in a config file")

    if not url:
        abort("Please specify a url or add it approprietly in a config file: projects.%s.url" % project_name)

    name = project_name if branch is None else project_name+"_"+branch

    # use existing stack only (create one manually)
    new_stack = Stack(domain, stack_version, meta_path=meta_path)
    if not new_stack.is_persisted():
        abort("""Please create a new stack first, using: `gachette stack_create`""")

    # Checkout specific branch and build
    wc = WorkingCopy(name)
    wc.prepare_environment()
    wc.checkout_working_copy(url, branch)

    # set version based on the git commit
    suffix = "" if branch is None else branch
    version = wc.get_version_from_git(suffix=suffix)
    wc.set_version(app=version, env=version, service=version)

    results = wc.build(debs_path, path_to_missile)
    print "results: ", results
    # TODO extract package build results properly
    for item in results:
        new_stack.add_package(item['name'], item['version'], item['file_name'])


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
