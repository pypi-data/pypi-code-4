# Create your views here.
from django.views.generic import DetailView, ListView, FormView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.db import transaction

from .models import Timeline, TimelineImporter
from .forms import TimelineForm

class TimelineListView(ListView):
    """List timelines."""
    context_object_name='timelines'
    template_name = 'timelinejs/timelines.html'

    def get_queryset(self):
        return Timeline.objects.visible_to_user(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TimelineListView, self).get_context_data(**kwargs)
        context['user_can_add_timelines'] = False
        if self.request.user.is_staff and self.request.user.has_perm('timelinejs.add_timeline'):
            context['user_can_add_timelines'] = True
        return context

class TimelineDetailView(DetailView):
    """Show a timeline."""
    template_name = 'timelinejs/timeline.html'

    def get_object(self):
        return Timeline.objects.get_visible_to_user_or_404(
                user=self.request.user,
                slug=self.kwargs['slug'])

class ImportTimelineFromSpreadsheetView(FormView):
    """Import a timeline from a Google spreadsheet."""
    form_class = TimelineForm
    template_name = 'timelinejs/import_timeline.html'

    @method_decorator(permission_required('timelinejs.add_timeline'))
    def dispatch(self, *args, **kwargs):
        return super(ImportTimelineFromSpreadsheetView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        with transaction.commit_manually():
            timeline = form.save(commit=False)
            timeline.slug = slugify(timeline.title)
            timeline.save()
            self.timeline = timeline
            try:
                importer = TimelineImporter(form.cleaned_data['item_data'], timeline)
                recoverable_errors = importer.import_items()
            except Exception, e:
                messages.add_message(self.request, messages.ERROR, 'Importing your timeline data failed with error: %s. You may be able to fix this by editing the spreadsheet you are trying to import.' % e)
                transaction.rollback()
                return self.form_invalid(form)
            # simply warn user of recoverable errors in the spreadsheet that were ignored
            for error in recoverable_errors:
                messages.add_message(self.request, messages.WARNING, error)
            transaction.commit()
        return super(ImportTimelineFromSpreadsheetView, self).form_valid(form)

    def get_success_url(self):
        return self.timeline.get_absolute_url()
