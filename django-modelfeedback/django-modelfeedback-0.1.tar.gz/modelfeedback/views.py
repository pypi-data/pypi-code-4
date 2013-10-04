from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from modelfeedback.models import Feedback
from modelfeedback.forms import FeedbackForm


class FeedbackDetailView(DetailView):
    model = Feedback


class FeedbackCreateView(CreateView):
    model = Feedback
    form_class = FeedbackForm

    def form_valid(self, form):
        messages.success(self.request, _('Thank you for your feedback!'))
        return super(FeedbackCreateView, self).form_valid(form)

    def get_target(self):
        try:
            content_type = ContentType.objects.get_by_natural_key(
                self.kwargs.get('app_label'),
                self.kwargs.get('model'))
            target = content_type.get_object_for_this_type(
                pk=self.kwargs.get('object_id'))
        except ObjectDoesNotExist:
            raise Http404
        return target

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FeedbackCreateView, self).get_form_kwargs(*args,
                                                                 **kwargs)
        kwargs.update({
            'user': self.request.user,
            'instance': Feedback.create(self.request.user, self.get_target()),
        })
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedbackCreateView, self).dispatch(*args, **kwargs)


class FeedbackDetailMixin(object):
    def get_rating_data(self):
        obj = self.get_object()
        rating_data = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}

        rating_queryset = Feedback.objects.filter(
            object_id=obj.id,
            content_type=ContentType.objects.get_for_model(obj)) \
            .values('rating').annotate(Count('rating')).order_by('-rating')

        for rating_count in rating_queryset:
            rating_data.update({
                rating_count.get('rating'): rating_count.get('rating__count'),
            })

        return rating_data

    def get_context_data(self, **kwargs):
        context_data = super(FeedbackDetailMixin,
                             self).get_context_data(**kwargs)
        context_data.update({'rating_data': self.get_rating_data()})
        return context_data
