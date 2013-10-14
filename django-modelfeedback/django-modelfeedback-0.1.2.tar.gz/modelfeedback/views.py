from __future__ import division
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
    app_label_url_kwarg = 'app_label'
    model_url_kwarg = 'model'
    target_pk_url_kwarg = 'target_pk'

    def form_valid(self, form):
        messages.success(self.request, _('Thank you for your feedback!'))
        return super(FeedbackCreateView, self).form_valid(form)

    def get_success_url(self):
        try:
            return self.target.get_absolute_url()
        except AttributeError:
            return super(FeedbackCreateView, self).get_success_url()

    def get_target(self):
        try:
            content_type = ContentType.objects.get_by_natural_key(
                self.kwargs.get(self.app_label_url_kwarg),
                self.kwargs.get(self.model_url_kwarg))
            target = content_type.get_object_for_this_type(
                pk=self.kwargs.get(self.target_pk_url_kwarg))
        except ObjectDoesNotExist:
            raise Http404
        return target

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FeedbackCreateView, self).get_form_kwargs(*args,
                                                                 **kwargs)
        kwargs.update({
            'instance': Feedback.create(self.request.user, self.target),
        })
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeedbackCreateView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.target = self.get_target()
        return super(FeedbackCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.target = self.get_target()
        return super(FeedbackCreateView, self).post(request, *args, **kwargs)


class RatingAggregatedData(object):
    count = 0
    average = 0
    data = {}

    def __init__(self, *args, **kwargs):
        self.data = dict([(5-x, {'count': 0,
                                 'percent': 0,
                                 'score': 5-x}) for x in range(5)])

    def update(self, rating, count):
        self.data.get(rating)['count'] = count
        total = self.count = self.average = 0

        for score, data in self.data.iteritems():
            self.count += data['count']
            total += data['count']*score

        for score, data in self.data.iteritems():
            self.data.get(score)['percent'] = \
                (data['count']*100)//self.count

        self.average = round(total / self.count, 1)


class RatingDataMixin(object):
    def get_rating_data(self, obj):
        rating_data = RatingAggregatedData()

        rating_queryset = Feedback.objects.filter(
            object_id=obj.id,
            content_type=ContentType.objects.get_for_model(obj)) \
            .values('rating').annotate(Count('rating')).order_by('-rating')

        for rating_count in rating_queryset:
            rating_data.update(rating_count.get('rating'),
                               rating_count.get('rating__count'))

        return rating_data


class FeedbackDetailMixin(RatingDataMixin):
    def get_context_data(self, **kwargs):
        context_data = super(FeedbackDetailMixin,
                             self).get_context_data(**kwargs)

        context_data.get('object').rating_data = \
            self.get_rating_data(self.object)

        return context_data


class FeedbackListMixin(RatingDataMixin):
    def get_context_data(self, **kwargs):
        context_data = super(FeedbackListMixin,
                             self).get_context_data(**kwargs)

        for obj in context_data.get('object_list'):
            obj.rating_data = self.get_rating_data(obj)

        return context_data
