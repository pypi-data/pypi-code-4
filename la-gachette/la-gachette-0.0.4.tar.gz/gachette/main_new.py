#!/usr/bin/env python
#code: utf-8

from fabric.api import task

from lib.working_copy import WorkingCopy
from lib.stack import Stack
from lib import get_version

api_url = "http://192.168.3.1:5000/api/stack/"


class RedisStackOperator(redis_client):
    def __init__(self, api_url):
        self.api_url = api_url

    def get_reference_package_folder(self, name, version):
        return os.path.join(self.target_folder, "packages", name, "version", version)

    def get_stack_folder(self, stack_version):
        return os.path.join(self.target_folder, "stacks", stack_version)

    def get_stack_package_folder(self, stack_version, pkg_name):
        return os.path.join(self.get_stack_folder(stack_version), "packages", pkg_name)

    def test_stack_exists(self, stack):
        """
        Check if stack folder exists on the filesystem.
        """
        stack_path = self.get_stack_folder(stack.version)

        with settings(warn_only=True):
            if run("test -d %s" % stack_path).failed:
                return False
        
        return True

    def copy_old_stack(self, ld_stack, new_stack):
        """
        Copy stack folder into new one.
        """
        new_stack_path = self.get_stack_folder(new_stack.version)
        old_stack_path = self.get_stack_folder(old_stack.version)

        run("mkdir -p %s" % new_stack_path)
        run("cp -R %s/* %s" % (old_stack_path, new_stack_path))


    def persist_stack(self, new_stack):
        """
        Create empty folder.
        """
        new_stack_path = self.get_stack_folder(new_stack.version)
        run("mkdir -p %s/packages/" % new_stack_path)
        

    def add_reference_package(self, name, version, file_name):
        """
        Register this package in the references packages tree
        """
        folder_dst = self.get_reference_package_folder(name, version)
        run("mkdir -p %s" % folder_dst)
        run("echo %s > %s/file" % (file_name, folder_dst))


    def add_stack_package(self, stack, pkg_name, pkg_version):
        """
        Registers a built package in the stack.
        """
        folder_dst = self.get_stack_package_folder(stack.version, pkg_name)
        run("mkdir -p %s" % folder_dst)
        run("echo %s > %s/version" % (pkg_version, folder_dst))

@task
def create_stack(domain, name=None, from_stack=None):
    """
    """
    # come from configuration
    #operator = FSStackOperator(meta_path)
    operator = RedisStackOperator(api_url)

    if not name:
        name = operator.get_next_stack_name(domain)
        stack = Stack(domain, name, operator=operator)
    elif name and from_stack:
        stack = Stack(domain, name, operator=operator)
        stack.clone_from(from_stack)
    elif name:
        stack = Stack(domain, name, operator=operator)

    print "Stack created ", stack

    return stack

@task
def add_to_stack(domain, stack, project, stack=None, branch=None, url=url):
    """
    """
    # come from configuration
    #operator = FSStackOperator(meta_path)
    operator = RedisStackOperator(api_url)

    new_stack = Stack(domain, stack, operator=operator)

    # Checkout specific branch and build
    wc = WorkingCopy(project)
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

