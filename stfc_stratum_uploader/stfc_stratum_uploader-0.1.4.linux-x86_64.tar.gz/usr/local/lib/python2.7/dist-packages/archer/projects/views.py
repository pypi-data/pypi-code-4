import logging
import os
from pprint import pformat
import shutil
import re

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template import loader
from guardian.decorators import permission_required_or_403
from django.template.context import RequestContext
from django.views.generic import View
import guardian.shortcuts

from archer.core.decorators import class_view_decorator
from archer.projects.forms import UploadFileForm, MakeDirectoryForm, RemoveDirectoryForm, RemoveFileForm
from archer.projects.models import Project
from archer.packages.models import Package
from archer.core import exceptions


NUMBER_OF_PACKAGES = 5

logger = logging.getLogger(__name__)


def unauthenticated(request):
    return render(request, 'unauthenticated.html')


def get_objects_for_user(user, perms, klass=None, use_groups=True, any_perm=False):
    if user.is_authenticated():
        return guardian.shortcuts.get_objects_for_user(user, perms, klass, use_groups, any_perm)
    return []


def index(request):
    debug_info = {'user': pformat(request.user.__dict__),
                  'environ': pformat(dict(os.environ.items())),
                  'meta': pformat(dict(request.META))}
    projects = get_objects_for_user(request.user, 'projects.view_project')
    package_sets = [(project,
                     request.user.has_perm('projects.upload_package', project),
                     [package for package in project.package_set.order_by('-id')],
                    ) for project in projects]
    context = {'package_sets': package_sets, 'debug_info': debug_info}
    return render(request, 'projects/index.html', context)


@class_view_decorator(permission_required_or_403('projects.upload_package', (Project, 'pk', 'project_id')))
class UploadView(View):
    def get(self, request, project_id):
        form = UploadFileForm()
        return render_to_response('projects/upload.html',
                                  {'form': form, 'project_id': project_id},
                                  context_instance=RequestContext(request))

    def post(self, request, project_id):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            from guardian.shortcuts import assign_perm
            # handle files
            logger.debug(pformat(form))
            package = form.save(commit=False)
            package.status = Package.Status.uploaded
            package.project_id = project_id
            package.save()
            assign_perm('packages.deploy_package', request.user, package)
            assign_perm('packages.remove_package', request.user, package)
            return HttpResponseRedirect(reverse('projects:show', args=[project_id]))
        return render_to_response('projects/upload.html',
                                  {'form': form, 'project_id': project_id},
                                  context_instance=RequestContext(request))


class ModifyDirectory(View):
    def validate_directory(self, project_id, path):
        project, full_path = self.__validate_format(project_id, path)
        if not os.path.isdir(full_path):
            raise exceptions.ArgumentError('"%s" is not a directory' % full_path)
        if not os.path.exists(full_path):
            raise exceptions.ArgumentError('Directory "%s" does not exist' % full_path)
        return project, full_path

    def validate_file(self, project_id, path):
        project, full_path = self.__validate_format(project_id, path)
        if not os.path.isfile(full_path):
            raise exceptions.ArgumentError('"%s" is not a file' % full_path)
        if not os.path.exists(full_path):
            raise exceptions.ArgumentError('File "%s" does not exist' % full_path)
        return project, full_path

    def __validate_format(self, project_id, path):
        if path.startswith('/'):
            raise exceptions.ValidationError('File or directory "%s" cannot start with "/"' % path)
        project = get_object_or_404(Project, pk=project_id)
        if re.search('(\.\./|/\.\.)', path):
            raise exceptions.ValidationError('File or directory "%s" contains ".."' % path)
        full_path = os.path.join(project.full_path(), path)
        return project, full_path

# TODO: use django forms
@permission_required_or_403('projects.deploy_package', (Project, 'pk', 'project_id'))
def deploy(request, project_id, path):
    def validate():
        if path.startswith('/'):
            raise exceptions.ValidationError('Directory "%s" cannot start with "/"' % path)
        project = get_object_or_404(Project, pk=project_id)
        if re.search('(\.\./|/\.\.)', path):
            raise exceptions.ValidationError('%s contains ".."' % path)
        project_path = project.full_path()
        parent_directory = os.path.join(project_path, path)
        # if os.path.commonprefix([parent_directory, project_path]) != project_path:
        #     raise
        if not os.path.isdir(parent_directory):
            raise exceptions.ArgumentError('"%s" is not a directory' % parent_directory)
        if not os.path.exists(parent_directory):
            raise exceptions.ArgumentError('"%s" does not exist' % parent_directory)
        return project, parent_directory

    validate()
    if request.POST:
        if 'package' not in request.POST:
            return HttpResponseBadRequest()
        if not request.POST['package'].isdigit():
            messages.add_message(request, messages.ERROR,
                                 'package with id = "%s" does not exist!' % request.POST['package'])
            return HttpResponseRedirect(reverse('projects:deploy', args=[project_id, path]))
        package_id = request.POST['package']
        package = Package.objects.get(pk=package_id)

        if package.can_deploy():
            if request.user.has_perm('packages.deploy_package', package):
                try:
                    deployed = package.deploy(path)
                    if deployed:
                        messages.add_message(request, messages.SUCCESS,
                                             'Package "%s" successfully deployed in "%s" directory' % (package, path))
                    else:
                        messages.add_message(request, messages.ERROR, 'Cannot deploy a package "%s"!' % package)
                except (IOError, exceptions.ValidationError, OSError) as e:
                    messages.add_message(request, messages.ERROR,
                                         'Error while deploying a package "%s": "%s"' % (package, e))
            else:
                messages.add_message(request, messages.ERROR,
                                     'Does not have permission to deploy package "%s"!' % package)
        else:
            messages.add_message(request, messages.ERROR, 'Cannot deploy a package "%s"!' % package)
        return HttpResponseRedirect(reverse('projects:show', args=[project_id]))

    else:
        projects_packages = Package.objects.filter(project_id=project_id)
        packages = [package for package in projects_packages if
                    request.user.has_perm('packages.deploy_package', package) and package.can_deploy()
        ]
        return render_to_response('projects/deploy.html',
                                  {'packages': packages,
                                   'project_id': project_id,
                                   'path': path,
                                  },
                                  context_instance=RequestContext(request))


class Remove(ModifyDirectory):
    def _get(self, request, project, path, to_remove,
             form_class=RemoveDirectoryForm,
             template='projects/rmdir.html',
             text='directory'):
        form = form_class(to_remove)
        try:
            return render_to_response(template,
                                      {'project_id': project.id,
                                       'form': form,
                                       'path': path,
                                      },
                                      context_instance=RequestContext(request))
        except exceptions.ApplicationError as e:
            messages.add_message(request, messages.ERROR, 'Could not delete %s: %s' % (text, e))
            return HttpResponseRedirect(reverse('projects:show', args=[project.id]))

    def _post(self, request, project, path, to_remove,
              form_class=RemoveDirectoryForm,
              template='',
              text='directory'):
        form = form_class(to_remove, request.POST)
        try:
            if os.path.isdir(to_remove):
                shutil.rmtree(to_remove)
            elif os.path.isfile(to_remove):
                os.remove(to_remove)
            else:
                raise exceptions.ArgumentError('How did that happen? Not a file nor directory!')
            messages.add_message(request, messages.SUCCESS,
                                 '%s "%s" successfully removed.' % (text.title(), to_remove))
        except (exceptions.ApplicationError, OSError) as e:
            messages.add_message(request, messages.ERROR,
                                 'Could not delete %s "%s": %s' % (text, to_remove, e))
        return HttpResponseRedirect(reverse('projects:show', args=[project.id]))


@class_view_decorator(permission_required_or_403('projects.remove_file', (Project, 'pk', 'project_id')))
class RemoveFile(Remove):
    def get(self, request, project_id, path):
        project, to_remove = self.validate_file(project_id, path)
        return super(RemoveFile, self)._get(request, project, path, to_remove,
                                            form_class=RemoveFileForm,
                                            template='projects/rm.html',
                                            text='file')

    def post(self, request, project_id, path):
        project, to_remove = self.validate_file(project_id, path)
        return super(RemoveFile, self)._post(request, project, path, to_remove,
                                             form_class=RemoveFileForm,
                                             template='projects/rm.html',
                                             text='file')


@class_view_decorator(permission_required_or_403('projects.remove_directory', (Project, 'pk', 'project_id')))
class RemoveDirectory(Remove):
    def get(self, request, project_id, path):
        project, to_remove = self.validate_directory(project_id, path)
        return super(RemoveDirectory, self)._get(request, project, path, to_remove,
                                                 form_class=RemoveDirectoryForm,
                                                 template='projects/rmdir.html',
                                                 text='directory')

    def post(self, request, project_id, path):
        project, to_remove = self.validate_directory(project_id, path)
        return super(RemoveDirectory, self)._post(request, project, path, to_remove,
                                                  form_class=RemoveDirectoryForm,
                                                  template='projects/rmdir.html',
                                                  text='directory')


@class_view_decorator(permission_required_or_403('projects.make_directory', (Project, 'pk', 'project_id')))
class MakeDirectory(ModifyDirectory):
    def get(self, request, project_id, path):
        project, parent = self.validate_directory(project_id, path)
        form = MakeDirectoryForm(parent)
        return render_to_response('projects/mkdir.html',
                                  {'project_id': project.id,
                                   'form': form,
                                   'path': path,
                                  },
                                  context_instance=RequestContext(request))

    def post(self, request, project_id, path):
        project, parent = self.validate_directory(project_id, path)
        form = MakeDirectoryForm(parent, request.POST)
        if form.is_valid():
            try:
                new_directory = request.POST['new_directory']
                dir_full_path = os.path.join(parent, new_directory)
                os.mkdir(dir_full_path, 00755)
                messages.add_message(request, messages.SUCCESS,
                                     'Directory "%s" successfully created.' % dir_full_path)
            except OSError as e:
                messages.add_message(request, messages.ERROR,
                                     'Could not create directory "%s": %s' % (dir_full_path, e))
            return HttpResponseRedirect(reverse('projects:show', args=[project_id]))
        return render_to_response('projects/mkdir.html',
                                  {'form': form,
                                   'path': path,
                                   'project_id': project.id},
                                  context_instance=RequestContext(request))


@permission_required_or_403('projects.view_project', (Project, 'pk', 'project_id'))
def show(request, project_id, path=''):
    SHOW_PRE_FILES_THRESHOLD = 100

    project = Project.objects.get(pk=project_id)
    can_upload = request.user.has_perm('projects.upload_package', project)
    can_deploy = request.user.has_perm('projects.deploy_package', project)
    path = project.full_path()

    def index_maker():
        def _index(root):
            files = os.listdir(root)
            files_only = []
            relative_path = ''
            for mfile in files:
                full_file_path = os.path.join(root, mfile)
                t = os.path.join(root, mfile)
                if os.path.isdir(t):
                    relative_path = full_file_path[len(path) + 1:]
                    yield loader.render_to_string('tree/_folder.html',
                                                  {'file': mfile + '/',
                                                   'subfiles': _index(os.path.join(root, t)),
                                                   'can_upload': can_upload,
                                                   'can_deploy': can_deploy,
                                                   'project_id': project_id,
                                                   'full_path': full_file_path,
                                                   'path': relative_path,
                                                  })
                    continue
                files_only += [mfile]
            if len(files_only) > 0:
                pre = len(files_only) > SHOW_PRE_FILES_THRESHOLD
                relative_path = root[len(path) + 1:]
                if pre:
                    files_only = "\n".join(files_only)
                yield loader.render_to_string('tree/_files.html',
                                              {'files': files_only,
                                               'project_id': project_id,
                                               'path': relative_path,
                                               'pre': pre,
                                              })

        if not os.path.isdir(path):
            return None
        return _index(path)

    return render_to_response('projects/show.html',
                              {'project': project,
                               'can_upload': can_upload,
                               'can_deploy': can_deploy,
                               'packages': [package for package in project.package_set.order_by('-id')],
                               'files': index_maker(),
                               'path': path,
                              },
                              context_instance=RequestContext(request))