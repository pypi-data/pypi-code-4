# -*- coding: utf-8 -*-
"""Here are defined Python functions of views.
Views are binded to URLs in :mod:`.urls`.
"""
import datetime
import json
import mimetypes
import os
import re
import stat
import tarfile
import zipfile
import tempfile
from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.urlresolvers import reverse
from django.db.models import F, Count, Q
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseNotModified, StreamingHttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.text import slugify
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.static import was_modified_since
from updoc.models import UploadDoc, Keyword, LastDocs
from updoc.process import process_new_file
from updoc.utils import list_directory

__author__ = "flanker"


class FileUploadForm(forms.Form):
    """Upload form"""
    file = forms.FileField(label=_('file'), max_length=255)


class SearchForm(forms.Form):
    """Upload form"""
    search = forms.CharField(max_length=255)


class UploadForm(forms.Form):
    """Upload form"""
    uid = forms.CharField(widget=forms.widgets.HiddenInput())
    id = forms.IntegerField(widget=forms.widgets.HiddenInput())
    name = forms.CharField(label=_('Name'), max_length=240)
    keywords = forms.CharField(label=_('Keywords'), max_length=255, required=False)


@csrf_exempt
@login_required(login_url='/login')
@permission_required('updoc.add_uploaddoc')
def upload_doc(request):
    form = FileUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        raise PermissionDenied
    obj = process_new_file(request.FILES['file'], request)
    basename = os.path.basename(request.FILES['file'].name).rpartition('.')[0]
    if basename[-4:] == '.tar':
        basename = basename[:-4]

    class FilledUploadForm(forms.Form):
        """Upload form"""
        uid = forms.CharField(widget=forms.widgets.HiddenInput(), initial=obj.uid)
        id = forms.IntegerField(widget=forms.widgets.HiddenInput(), initial=obj.id)
        name = forms.CharField(label=_('Name'), max_length=240, initial=basename,
                               widget=forms.widgets.TextInput(attrs={'placeholder': _('Please enter a name'), }))
        keywords = forms.CharField(label=_('Keywords'), max_length=255, required=False,
                                   widget=forms.widgets.TextInput(attrs={'placeholder': _('Please enter some keywords'),
                                                                         }))

    form = FilledUploadForm()
    template_values = {'form': form, }
    return render_to_response('upload_doc.html', template_values, RequestContext(request))


@login_required(login_url='/login')
def upload(request):
    """Index view, displaying and processing a form."""
    user = request.user if request.user.is_authenticated() else None
    if request.method == 'POST':
        form = UploadForm(request.POST)
        if form.is_valid():  # pylint: disable=E1101
            messages.info(request, _('File successfully uploaded'))
            obj = get_object_or_404(UploadDoc, uid=form.cleaned_data['uid'], id=form.cleaned_data['id'], user=user)
            obj.name = form.cleaned_data['name']
            for keyword in form.cleaned_data['keywords'].lower().split():
                obj.keywords.add(Keyword.get(keyword))
            obj.save()
            return HttpResponseRedirect(reverse('updoc.views.upload'))
        else:
            obj = get_object_or_404(UploadDoc, uid=form.cleaned_data['uid'], id=form.cleaned_data['id'], user=user)
            obj.delete()
            messages.error(request, _('Unable to upload this file'))
    else:
        form = FileUploadForm()
    template_values = {'form': form, 'title': _('Upload a new file')}
    template_values.update(csrf(request))  # prevents cross-domain requests
    return render_to_response('upload.html', template_values, RequestContext(request))


DAY = datetime.timedelta(1)


def my_docs(request):
    user = request.user if request.user.is_authenticated() else None
    uploads = UploadDoc.objects.filter(user=user).order_by('-upload_time').select_related()
    template_values = {'uploads': uploads, 'title': _('My documents')}
    return render_to_response('my_docs.html', template_values, RequestContext(request))


def delete_doc(request, doc_id):
    user = request.user if request.user.is_authenticated() else None
    obj = get_object_or_404(UploadDoc, id=doc_id)
    if not request.user.is_superuser and obj.user != user:
        raise PermissionDenied
    name = obj.name
    try:
        obj.delete()
        messages.info(request, _('%(doc)s successfully deleted') % {'doc': name})
    except IOError:
        messages.error(request, _('Unable to delete %(doc)s ') % {'doc': name})
    return HttpResponseRedirect(reverse('updoc.views.index'))


@csrf_exempt
def edit_doc(request, doc_id):
    name = request.POST.get('name')
    keywords = request.POST.get('keywords')
    user = request.user if request.user.is_authenticated() else None
    obj = get_object_or_404(UploadDoc, id=doc_id)
    if not request.user.is_superuser and obj.user != user:
        raise PermissionDenied
    if name:
        if obj.name != name.strip():
            obj.name = name.strip()
        obj.save()
    if keywords is not None:
        obj.keywords.clear()
        for keyword in keywords.lower().split():
            if keyword:
                obj.keywords.add(Keyword.get(keyword))
        obj.save()
    return HttpResponse(json.dumps({'ok': True}), content_type='application/json')


range_re = re.compile(r'bytes=(\d+)-(\d+)')


def static_serve(request, path, document_root=None):
    if document_root is None:
        document_root = settings.STATIC_ROOT
    filename = os.path.abspath(os.path.join(document_root, path))
    if not filename.startswith(document_root):
        raise Http404
    if settings.USE_XSENDFILE:
        return xsendfile(request, filename)
    return sendfile(request, filename)


def xsendfile(request, filename):
    response = HttpResponse()
    response['X-Sendfile'] = filename.encode('utf-8')
    return response


def sendfile(request, filename):
    # Respect the If-Modified-Since header.
    if not os.path.isfile(filename):
        raise Http404
    statobj = os.stat(filename)
    if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                              statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
        return HttpResponseNotModified()
    content_type = mimetypes.guess_type(filename)[0]
    range_ = request.META.get('HTTP_RANGE', '')
    t = range_re.match(range_)
    size = os.path.getsize(filename)
    start = 0
    end = size - 1
    if t:
        start, end = int(t.group(1)), int(t.group(2))
    if end - start + 1 < size:
        obj = open(filename, 'rb')
        obj.seek(start)
        response = HttpResponse(obj.read(end - start + 1), content_type=content_type, status=206)
        response['Content-Range'] = 'bytes %d-%d/%d' % (start, end, size)
    else:
        obj = open(filename, 'rb')
        return StreamingHttpResponse(obj, content_type=content_type)
    response['Content-Length'] = end - start + 1
    #response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    return response


def compress_archive(request, doc_id, fmt='zip'):
    tmp_file = tempfile.NamedTemporaryFile()
    doc = get_object_or_404(UploadDoc, id=doc_id)
    arc_root = slugify(doc.name)
    if fmt == 'zip':
        cmp_file = zipfile.ZipFile(tmp_file, mode='w', compression=zipfile.ZIP_DEFLATED)
        for (root, dirnames, filenames) in os.walk(doc.path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                arcname = os.path.join(arc_root, os.path.relpath(full_path, doc.path))
                cmp_file.write(full_path, arcname)
        content_type = 'application/zip'
    elif fmt in ('gz', 'bz2', 'xz'):
        cmp_file = tarfile.open(name=arc_root + '.tar.' + fmt, mode='w:' + fmt, fileobj=tmp_file)
        for filename in os.listdir(doc.path):
            full_path = os.path.join(doc.path, filename)
            arcname = os.path.join(arc_root, os.path.relpath(full_path, doc.path))
            cmp_file.add(full_path, arcname)
        content_type = 'application/x-tar'
    else:
        raise ValueError
    cmp_file.close()
    tmp_file.seek(0)
    return StreamingHttpResponse(tmp_file, content_type=content_type)


def show_doc(request, doc_id, path=''):
    doc = get_object_or_404(UploadDoc, id=doc_id)
    root_path = doc.path
    full_path = os.path.join(root_path, path)
    if not full_path.startswith(root_path):
        raise Http404
    user = request.user if request.user.is_authenticated() else None
    if path == '':
        checked, created = LastDocs.objects.get_or_create(user=user, doc=doc)
        if not created:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            LastDocs.objects.filter(user=user, doc=doc).update(count=F('count') + 1, last=now)
    if not os.path.isfile(full_path):
        directory = list_directory(root_path, path, 'updoc.views.show_doc', view_arg='path',
                                   view_kwargs={'doc_id': doc.id}, dir_view_name='updoc.views.show_doc',
                                   dir_view_arg='path', dir_view_kwargs={'doc_id': doc.id}, show_files=True,
                                   show_dirs=True, show_parent=True, show_hidden=False)
        editable = request.user.is_superuser or request.user == doc.user
        template_values = {'directory': directory, 'doc': doc, 'editable': editable, 'title': str(doc),
                           'keywords': ' '.join([keyword.value for keyword in doc.keywords.all()])}
        return render_to_response('list_dir.html', template_values, RequestContext(request))
    elif settings.USE_XSENDFILE:
        return xsendfile(request, full_path)
    return sendfile(request, full_path)


def index(request):
    """Index view, displaying and processing a form."""

    user = request.user if request.user.is_authenticated() else None
    yesterday = datetime.datetime.utcnow().replace(tzinfo=utc) - DAY
    search = SearchForm(request.GET)
    if search.is_valid():
        pattern = search.cleaned_data['search']
        if len(pattern) > 3:
            docs = UploadDoc.objects.filter(Q(name__icontains=pattern) | Q(keywords__value__icontains=pattern))
        else:
            docs = UploadDoc.objects.filter(Q(name__iexact=pattern) | Q(keywords__value__iexact=pattern))
        template_values = {'uploads': docs.distinct().select_related(), 'title': _('Search results')}
        return render_to_response('my_docs.html', template_values, RequestContext(request))
    keywords_with_counts = Keyword.objects.all().annotate(count=Count('uploaddoc')).filter(count__gt=0)\
        .order_by('-count')[0:15]
    recent_uploads = UploadDoc.objects.filter(upload_time__gte=yesterday).order_by('-upload_time')[0:5]
    recent_checked = LastDocs.objects.filter(user=user).select_related().order_by('-last')[0:20]
    template_values = {'recent_checked': recent_checked, 'title': _('Updoc'),
                       'recent_uploads': recent_uploads, 'search': search, 'keywords': keywords_with_counts}
    return render_to_response('index.html', template_values, RequestContext(request))
