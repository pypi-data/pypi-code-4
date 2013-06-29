import urllib

from pygments import highlight
from pygments.lexers import DiffLexer
from pygments.formatters import HtmlFormatter

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from staging.models import StagingServer
from staging.utils import staging_manager
from player.player_staging.forms import StagingServerForm, CreateRepoFromServerForm


@login_required
def server_list(request):
    """ List Staging Servers stored in database """
    server_list = StagingServer.objects.all()
    return render_to_response('player_staging/server_list.html', {'server_list': server_list},
                              context_instance=RequestContext(request))


@login_required
def server_add(request, server=None):
    """ Add a new Staging Server to store in database """
    if request.method == 'POST':
        form = StagingServerForm(request.POST, instance=server)
        if form.is_valid():
            server = form.save()
            msg = server and _(u'The Staging Server was successfully modified') or \
                  _(u'The Staging Server was successfully added')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('server_detail', args=(server.id, )))
    else:
        form = StagingServerForm(instance=server)
    return render_to_response(
        "player_staging/server_edit.html",
        {'form': form, 'server': server},
        context_instance=RequestContext(request),
    )


@login_required
def server_detail(request, server_id):
    """ View Staging Server """
    server = StagingServer.objects.get(pk=server_id)
    return render_to_response('player_staging/server_detail.html', {'server': server},
                              context_instance=RequestContext(request))


@login_required
def server_edit(request, server_id):
    """ Edit a Staging Server """
    server = get_object_or_404(StagingServer, pk=server_id)
    return server_add(request, server)


@login_required
def create_repo_from_server(request):
    if request.method == 'POST':
        form = CreateRepoFromServerForm(request.POST)
        if form.is_valid():
            url_path = reverse('download_repository')
            url = urllib.urlopen('http://%s%s' % (form.cleaned_data['hostname'], url_path))
            staging_manager.unbundle(url)
            msg = _(u'The repository was successfully fetched')
            messages.success(request, msg)
            return HttpResponseRedirect(reverse('publish'))
    else:
        form = CreateRepoFromServerForm()
    return render_to_response(
        "player_staging/create_repo_from_server.html",
        {'form': form},
        context_instance=RequestContext(request),
    )


@login_required
def publish(request):
    """ Show current version """
    revision = staging_manager.get_revision()
    uninitialized = revision.split('\n')[0].replace('changeset:', '').strip().startswith('-1')
    return render_to_response('player_staging/publish.html', {'revision': revision, 'uninitialized': uninitialized},
                              context_instance=RequestContext(request))


@login_required
def publish_new(request):
    """ Creates the new version """
    staging_manager.staging_export()
    diff = staging_manager.get_diff()
    removed = staging_manager.get_removed_files()
    added = staging_manager.get_added_files()
    return render_to_response('player_staging/publish_new.html', {'added': added, 'removed': removed,
                              'plain_diff': diff,
                              'diff': highlight(diff, DiffLexer(), HtmlFormatter()),
                              'style': HtmlFormatter().get_style_defs('.highlight')},
                              context_instance=RequestContext(request))


@login_required
def commit(request):
    """ Comit changes into staging """
    staging_manager.commit()
    return HttpResponseRedirect(reverse('publish'))


@login_required
def log_view(request):
    """ Creates the new version """
    commits = staging_manager.get_logs()
    return render_to_response('player_staging/log_view.html', {'commits': commits},
                              context_instance=RequestContext(request))


@login_required
def log_detail(request, changeset_id):
    """ Creates the new version """
    log = staging_manager.get_log_for_revision(changeset_id)
    return render_to_response('player_staging/log_detail.html', {'log': log, 'changeset': changeset_id,
                              'diff': highlight(log['diff'], DiffLexer(), HtmlFormatter()),
                              'style': HtmlFormatter().get_style_defs('.highlight')},
                              context_instance=RequestContext(request))


@login_required
def update_from_repository(request):
    """ Comit changes into staging """
    staging_manager.staging_import()
    msg = _(u'The website was successfully updated from local repository')
    messages.success(request, msg)
    return HttpResponseRedirect(reverse('publish'))
