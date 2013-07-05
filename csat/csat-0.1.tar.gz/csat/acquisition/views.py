from StringIO import StringIO
import logging
import os

from django.core.files.base import File, ContentFile
from django.views.generic import edit, list, base, detail
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.utils.timezone import now
from django.core.servers.basehttp import FileWrapper
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from csat import acquisition, client
from csat.graphml import builder
from . import models, forms


logger = logging.getLogger(__name__)


class SessionsIndex(list.ListView):
    template_name = 'csat/acquisition/session/list.html'
    model = models.AcquisitionSessionConfig
    context_object_name = 'sessions'

    def get_queryset(self):
        return self.model.objects.filter(temporary=False)

session_index = SessionsIndex.as_view()



def run_acquisition_session(request, session):
    session.started = now()

    collector_server = client.JsonRPCProxy(
        **settings.ACQUISITION_SERVER['private'])

    try:
        for collector in session.collectors.all():
            collector.get_collector().run(request, collector, collector_server)
    except client.CouldNotConnect:
        # TODO: Acquisition server offline
        raise

    graph = builder.GraphMLDocument()
    graph.attr(builder.Attribute.GRAPH, 'thumbnail')
    graph.graph()['thumbnail'] = session.get_thumbnail_url()
    fh = graph.to_file(StringIO())
    session.graph.save('graph', File(fh))

    session.save()


class SessionRun(detail.SingleObjectMixin, base.View):
    queryset = models.AcquisitionSessionConfig.objects.filter(temporary=False,
                                                              started=None)

    def get_success_url(self):
        return reverse('csat:acquisition:session', kwargs={
            'pk': self.object.pk
        })

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.started and self.object.collectors.count():
            run_acquisition_session(request, self.object)
        return HttpResponseRedirect(self.get_success_url())

session_run = SessionRun.as_view()


class SessionReset(detail.SingleObjectMixin, base.View):
    queryset = models.AcquisitionSessionConfig.objects.filter()

    def get_success_url(self):
        return reverse('csat:acquisition:session', kwargs={
            'pk': self.object.pk
        })

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.started = None
        self.object.completed = None
        self.object.thumbnail_background = None
        if self.object.thumbnail:
            self.object.thumbnail.delete(save=False)
        path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'no-thumb.png')
        with open(path) as fh:
            self.object.thumbnail.save('thumb', File(fh))
        self.object.thumbnail_background = self.object.get_thumbnail_background()
        if self.object.graph:
            self.object.graph.delete(save=False)
        for collector in self.object.collectors.all():
            collector.started = None
            collector.completed = None
            collector.running_instance_id = None
            collector.result_id = None
            collector.status = collector.READY
            if collector.graph:
                collector.graph.delete(save=False)
            if collector.output:
                collector.output.delete(save=False)
            collector.save()
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

session_reset = SessionReset.as_view()


class SessionDetails(detail.DetailView):
    queryset = models.AcquisitionSessionConfig.objects.filter(temporary=False)
    context_object_name = 'session'

    def get_template_names(self):
        if self.request.is_ajax():
            return ['csat/acquisition/session/_results.html']
        else:
            return ['csat/acquisition/session/details.html']

    def get_context_data(self, **kwargs):
        context = super(SessionDetails, self).get_context_data(**kwargs)
        context['acquisition_server'] = '{host}:{port}'.format(
            **settings.ACQUISITION_SERVER['public']
        )
        return context

session_view = SessionDetails.as_view()


class SessionEditor(edit.UpdateView):
    template_name = 'csat/acquisition/session/edit.html'
    form_class = forms.AcquisitionSessionConfigForm
    context_object_name = 'session'

    def get_queryset(self):
        return models.AcquisitionSessionConfig.objects.filter(
            started__isnull=True)

    def get_success_url(self):
        return reverse('csat:acquisition:session-edit', kwargs={
            'pk': self.object.pk
        })

    def get_form(self, form_class):
        form = super(SessionEditor, self).get_form(form_class)
        form.helper.form_action = reverse('csat:acquisition:session-edit',
                                          kwargs={'pk': self.object.pk})
        return form

    def get_context_data(self, **kwargs):
        #import time, random
        #time.sleep(random.random() * 5)
        context = super(SessionEditor, self).get_context_data(**kwargs)
        context['create'] = self.object.temporary == True
        context['collectors_types'] = acquisition.get_collectors()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.temporary = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_template_names(self):
        if self.request.is_ajax():
            return ['csat/acquisition/session/ajax_form.html']
        else:
            return super(SessionEditor, self).get_template_names()

session_edit = SessionEditor.as_view()


class SessionCreator(base.RedirectView):
    permanent = False
    query_string = False

    def get_redirect_url(self):
        session = models.AcquisitionSessionConfig.objects.create(
            temporary=True)
        path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'no-thumb.png')
        with open(path) as fh:
            session.thumbnail.save('thumb', File(fh))
        session.thumbnail_background = session.get_thumbnail_background()
        session.save()
        return reverse('csat:acquisition:session-edit', kwargs={
            'pk': session.pk
        })

session_create = SessionCreator.as_view()


class SessionDeletor(edit.DeleteView):
    template_name = 'csat/acquisition/session/delete.html'
    model = models.AcquisitionSessionConfig
    context_object_name = 'session'
    success_url = reverse_lazy('csat:acquisition:session-index')

    def get_context_data(self, **kwargs):
        context = super(SessionDeletor, self).get_context_data(**kwargs)
        context['prev'] = self.request.GET.get('prev', '')
        return context

session_delete = SessionDeletor.as_view()


class CollectorConfigCreate(edit.CreateView):
    template_name = 'csat/acquisition/session/ajax_form.html'

    def get_queryset(self):
        module = self.kwargs['collector']
        collector = acquisition.get_collector(module)
        return collector.get_model().objects.all()

    def get_form_class(self):
        module = self.kwargs['collector']
        collector = acquisition.get_collector(module)
        return collector.get_form()

    def get_form(self, form_class):
        #import time, random
        #time.sleep(random.random() * 5)
        form = super(CollectorConfigCreate, self).get_form(form_class)
        form.helper.form_action = reverse('csat:acquisition:collector-create',
                                          kwargs=self.kwargs)
        return form

    def get_context_data(self, **kwargs):
        module = self.kwargs['collector']
        context = super(CollectorConfigCreate, self).get_context_data(**kwargs)
        context['collector'] = acquisition.get_collector(module)
        return context

    def get_success_url(self):
        return reverse('csat:acquisition:collector-edit', kwargs={
            'session_pk': self.kwargs['session_pk'],
            'collector_pk': self.object.pk,
        })

    def form_invalid(self, form):
        return super(CollectorConfigCreate, self).form_invalid(form)

    def form_valid(self, form):
        session = get_object_or_404(models.AcquisitionSessionConfig,
                                    pk=int(self.kwargs['session_pk']))
        self.object = form.save(commit=False)
        self.object.configurator = self.kwargs['collector']
        self.object.session_config = session
        self.object.status = models.DataCollectorConfig.READY
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

collector_create = CollectorConfigCreate.as_view()


class CollectorConfigEdit(edit.UpdateView):
    template_name = 'csat/acquisition/session/ajax_form.html'
    pk_url_kwarg = 'collector_pk'

    def get_queryset(self):
        return models.DataCollectorConfig.objects.filter(
            session_config=int(self.kwargs['session_pk']))

    def get_form_class(self):
        collector = self.object.get_collector()
        return collector.get_form()

    def get_form(self, form_class):
        #import time, random
        #time.sleep(random.random() * 3)

        form = super(CollectorConfigEdit, self).get_form(form_class)
        form.helper.form_action = reverse('csat:acquisition:collector-edit',
                                          kwargs=self.kwargs)
        form.helper.attrs['data-deleteurl'] = reverse(
            'csat:acquisition:collector-remove',
            kwargs=self.kwargs
        )
        return form

    def get_context_data(self, **kwargs):
        context = super(CollectorConfigEdit, self).get_context_data(**kwargs)
        context['collector'] = self.object.get_collector()
        return context

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_response(self.get_context_data(form=form))

collector_edit = CollectorConfigEdit.as_view()


class CollectorConfigRemove(edit.DeleteView):
    pk_url_kwarg = 'collector_pk'

    def get_queryset(self):
        #import time, random
        #time.sleep(random.random() * 5)

        return models.DataCollectorConfig.objects.filter(
            session_config=int(self.kwargs['session_pk']))

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponse('')

collector_remove = CollectorConfigRemove.as_view()


class CollectorResult(edit.UpdateView):
    model = models.DataCollectorConfig
    form_class = forms.ResultsUploadForm
    template_name = 'csat/generic/simple-form.html'

    def get_success_url(self):
        return self.object.session_config.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(CollectorResult, self).get_context_data(**kwargs)
        context['page_title'] = 'Upload acquisition results'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        session = self.object.session_config

        # TODO: Validate graphml schema

        if form.cleaned_data['successful']:
            try:
                # TODO: Concurrency issue here!
                graph = builder.merge_files(
                    [self.request.FILES['graph']],
                    session.graph.path,
                )
                fh = graph.to_file(StringIO())
                if session.graph:
                    session.graph.delete(save=False)
                session.graph.save('graph', File(fh))
            except:
                ua = self.request.META.get('HTTP_USER_AGENT', '')
                if ua.startswith('CSAT Acquisition Server'):
                    self.object.set_failed()
                    raise
                else:
                    form._errors['graph'] = ['Invalid file.']
                    return self.form_invalid(form)
            else:
                self.object.save()
                self.object.set_completed()
        else:
            if 'graph' not in self.request.FILES:
                self.object.graph.save('graph', ContentFile(''))
            self.object.save()
            self.object.set_failed()

        if 'output' not in self.request.FILES:
            self.object.output.save('log', ContentFile(''))

        active_collectors = session.collectors
        active_collectors = active_collectors.exclude(
            status=models.DataCollectorConfig.FAILED)
        active_collectors = active_collectors.exclude(
            status=models.DataCollectorConfig.COMPLETED)

        if not active_collectors.count():
            session.set_completed()

        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        result_id = self.kwargs['result_id']
        try:
            return queryset.get(result_id=result_id,
                                status__in=(
                                    models.DataCollectorConfig.RUNNING,
                                    models.DataCollectorConfig.READY,
                                ))
        except models.DataCollectorConfig.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})

collector_upload_results = csrf_exempt(CollectorResult.as_view())


class FileViewer(base.TemplateResponseMixin, base.View):
    raw_format = 'txt'

    def get_template_names(self):
        return 'csat/generic/file-viewer.html'

    def is_raw_url(self):
        return self.kwargs['format'] != 'html'

    def get_raw_url(self):
        if self.is_raw_url():
            return self.request.get_full_path()
        else:
            url = self.request.get_full_path().split('?', 1)
            url[0] = url[0].rsplit('.', 1)[0] + '.' + self.raw_format
            return '?'.join(url)

    def get(self, request, *args, **kwargs):
        self.file = self.get_file()
        self.mime = self.get_mime()
        self.filename = self.get_filename()
        self.title = self.get_title()
        context = self.get_context_data()

        if not self.is_raw_url():
            # TODO: Limit big files
            context['raw_url'] = self.get_raw_url()
            max_length = 1024 * 50
            with self.file as fh:
                context['content'] = fh.read(max_length)
            context['truncated'] = len(context['content']) == max_length

            if context['truncated']:
                # Remove last line
                context['content'] = (context['content'].rsplit('\n', 1)[0]
                                      + '\n... [file truncated] ...')

            return self.render_to_response(context)
        else:
            if 'filename' in context and False:
                # Use x-sendfile (also check file.name)
                pass
            else:
                response = HttpResponse(FileWrapper(self.file),
                                        content_type=self.mime)
            if 'download' in self.request.GET:
                dispo = 'attachment; filename={}'.format(self.filename)
            else:
                dispo = 'inline; filename={}'.format(self.filename)
            response['Content-Disposition'] = dispo
            response['Content-Length'] = os.fstat(self.file.fileno()).st_size
            return response

    def get_mime(self):
        return 'text/plain'

    def get_title(self):
        return self.filename

    def get_filename(self):
        return self.file.name

    def get_context_data(self, **kwargs):
        return {
            'mime': self.mime,
            'title': self.title,
            'filename': self.filename,
        }


class CollectorViewLog(FileViewer):
    def get_title(self):
        return '{} logfile'.format(self.object.get_collector().name)

    def get_filename(self):
        return 'session_{}-collector_{}.log'.format(
            self.object.session_config.pk, self.object.pk)

    def get_file(self):
        queryset = models.DataCollectorConfig.objects.filter(
            session_config=int(self.kwargs['session_pk']))
        try:
            self.object = queryset.get(pk=int(self.kwargs['collector_pk']))
        except models.DataCollectorConfig.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return self.object.output

collector_view_log = CollectorViewLog.as_view(raw_format='txt')


class CollectorViewResults(FileViewer):
    def get_title(self):
        return 'Collected graph for {}'.format(
            self.object.get_collector().name)

    def get_mime(self):
        return 'application/xml'

    def get_filename(self):
        return 'session_{}-collector_{}.graphml'.format(
            self.object.session_config.pk, self.object.pk)

    def get_file(self):
        queryset = models.DataCollectorConfig.objects.filter(
            session_config=int(self.kwargs['session_pk']))
        try:
            self.object = queryset.get(pk=int(self.kwargs['collector_pk']))
        except models.DataCollectorConfig.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return self.object.graph

collector_view_results = CollectorViewResults.as_view(raw_format='graphml')


class SessionViewResults(FileViewer):
    def get_title(self):
        return 'Collected graph for session {}'.format(
            self.object.name)

    def get_mime(self):
        return 'application/xml'

    def get_filename(self):
        return 'session-{}-merged.graphml'.format(self.object.pk)

    def get_file(self):
        try:
            self.object = models.AcquisitionSessionConfig.objects.get(
                pk=int(self.kwargs['session_pk']))
        except models.DataCollectorConfig.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': models.AcquisitionSessionConfig._meta.verbose_name})
        return self.object.graph

session_view_results = SessionViewResults.as_view(raw_format='graphml')


class SessionThumbnail(detail.SingleObjectMixin, base.View):
    queryset = models.AcquisitionSessionConfig.objects.filter()

    def get(self, request, *args, **kwargs):
        session = self.get_object()
        if not session.thumbnail:
            path = os.path.join(os.path.dirname(__file__), 'static', 'images', 'no-thumb.png')
            with open(path) as fh:
                image = fh.read()
        else:
            with session.thumbnail as fh:
                image = fh.read()
        return HttpResponse(image, 'image/png')

    def post(self, request, *args, **kwargs):
        session = self.get_object()
        form = forms.ThumbnailForm(request.POST, request.FILES, instance=session)
        if form.is_valid():
            if session.thumbnail:
                session.thumbnail.delete(save=False)
            session = form.save(commit=False)
            session.thumbnail_background = session.get_thumbnail_background()
            session.save()
            return HttpResponse()
        else:
            return HttpResponseBadRequest()


session_thumbnail = csrf_exempt(SessionThumbnail.as_view())
