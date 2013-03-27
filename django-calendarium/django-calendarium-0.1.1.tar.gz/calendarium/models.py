"""
Models for the ``calendarium`` app.

The code of these models is highly influenced by or taken from the models of
django-schedule:

https://github.com/thauber/django-schedule/tree/master/schedule/models

"""
import json
from dateutil import rrule

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.utils.timezone import timedelta
from django.utils.translation import ugettext_lazy as _

from calendarium.constants import FREQUENCY_CHOICES, OCCURRENCE_DECISIONS
from calendarium.utils import OccurrenceReplacer
from calendarium.widgets import ColorPickerWidget
from south.modelsinspector import add_introspection_rules


class ColorField(models.CharField):
    """Custom color field to display a color picker."""
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 6
        super(ColorField, self).__init__(*args, **kwargs)
        self.validators.append(RegexValidator(
            regex='^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
            message='Only RGB color model inputs allowed, like 00000',
            code='nomatch'))

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorPickerWidget
        return super(ColorField, self).formfield(**kwargs)


add_introspection_rules([], ["^calendarium\.models\.ColorField"])


class EventModelManager(models.Manager):
    """Custom manager for the ``Event`` model class."""
    def get_occurrences(self, start, end):
        """Returns a list of events and occurrences for the given period."""
        # we always want the time of start and end to be at 00:00
        start = start.replace(minute=0, hour=0)
        end = end.replace(minute=0, hour=0)
        # if we recieve the date of one day as start and end, we need to set
        # end one day forward
        if start == end:
            end = start + timedelta(days=1)

        # retrieving relevant events
        # TODO currently for events with a rule, I can't properly find out when
        # the last occurrence of the event ends, or find a way to filter that,
        # so I'm still fetching **all** events before this period, that have a
        # end_recurring_period.
        # For events without a rule, I fetch only the relevant ones.
        qs = self.get_query_set()
        qs = qs.filter(start__lt=end)
        relevant_events = qs.filter(
            models.Q(end_recurring_period__isnull=True, end__gt=start) |
            models.Q(end_recurring_period__isnull=False))

        # get all occurrences for those events that don't already have a
        # persistent match and that lie in this period.
        all_occurrences = []
        for event in relevant_events:
            all_occurrences.extend(event.get_occurrences(start, end))

        # sort and return
        return sorted(all_occurrences, key=lambda x: x.start)


class EventModelMixin(models.Model):
    """
    Abstract base class to prevent code duplication.
    :start: The start date of the event.
    :end: The end date of the event.
    :creation_date: When this event was created.
    :description: The description of the event.

    """
    start = models.DateTimeField(
        verbose_name=_('Start date'),
    )

    end = models.DateTimeField(
        verbose_name=_('End date'),
    )

    creation_date = models.DateTimeField(
        verbose_name=_('Creation date'),
        auto_now_add=True,
    )

    description = models.TextField(
        max_length=2048,
        verbose_name=_('Description'),
        blank=True,
    )

    def __unicode__(self):
        return self.title

    class Meta:
        abstract = True


class Event(EventModelMixin):
    """
    Hold the information about an event in the calendar.

    :created_by: FK to the ``User``, who created this event.
    :category: FK to the ``EventCategory`` this event belongs to.
    :rule: FK to the definition of the recurrence of an event.
    :end_recurring_period: The possible end of the recurring definition.
    :title: The title of the event.

    """

    created_by = models.ForeignKey(
        'auth.User',
        verbose_name=_('Created by'),
        related_name='events',
    )

    category = models.ForeignKey(
        'EventCategory',
        verbose_name=_('Category'),
        related_name='events',
    )

    rule = models.ForeignKey(
        'Rule',
        verbose_name=_('Rule'),
        blank=True, null=True,
    )

    end_recurring_period = models.DateTimeField(
        verbose_name=_('End of recurring'),
        blank=True, null=True,
    )

    title = models.CharField(
        max_length=256,
        verbose_name=_('Title'),
    )

    objects = EventModelManager()

    def get_absolute_url(self):
        return reverse('calendar_event_detail', kwargs={'pk': self.pk})

    def _create_occurrence(self, occ_start, occ_end=None):
        """Creates an Occurrence instance."""
        # if the length is not altered, it is okay to only pass occ_start
        if not occ_end:
            occ_end = occ_start + (self.end - self.start)
        return Occurrence(
            event=self, start=occ_start, end=occ_end,
            # TODO not sure why original start and end also are occ_start/_end
            original_start=occ_start, original_end=occ_end,
            title=self.title, description=self.description,
            creation_date=self.creation_date, created_by=self.created_by)

    def _get_date_gen(self, rr, start, end):
        """Returns a generator to create the start dates for occurrences."""
        date = rr.after(start)
        while end and date <= end or not(end):
            yield date
            date = rr.after(date)

    def _get_occurrence_gen(self, start, end):
        """Computes all occurrences for this event from start to end."""
        # get length of the event
        length = self.end - self.start

        if self.rule:
            # if the end of the recurring period is before the end arg passed
            # the end of the recurring period should be the new end
            if self.end_recurring_period and end and (
                    self.end_recurring_period < end):
                end = self.end_recurring_period
            # making start date generator
            occ_start_gen = self._get_date_gen(
                self.get_rrule_object(),
                start - length, end)

            # chosing the first item from the generator to initiate
            occ_start = occ_start_gen.next()
            while not end or (end and occ_start <= end):
                occ_end = occ_start + length
                yield self._create_occurrence(occ_start, occ_end)
                occ_start = occ_start_gen.next()
        else:
            # check if event is in the period
            if (not end or self.start < end) and self.end >= start:
                yield self._create_occurrence(self.start, self.end)

    def get_occurrences(self, start, end=None):
        """Returns all occurrences from start to end."""
        # get persistent occurrences
        persistent_occurrences = self.occurrences.all()

        # setup occ_replacer with p_occs
        occ_replacer = OccurrenceReplacer(persistent_occurrences)

        # compute own occurrences according to rule that overlap with the
        # period
        occurrence_gen = self._get_occurrence_gen(start, end)
        # get additional occs, that we need to take into concern
        additional_occs = occ_replacer.get_additional_occurrences(
            start, end)
        occ = occurrence_gen.next()
        while not end or (occ.start < end or any(additional_occs)):
            if occ_replacer.has_occurrence(occ):
                p_occ = occ_replacer.get_occurrence(occ)

                # if the persistent occ falls into the period, replace it
                if (end and p_occ.start < end) and p_occ.end >= start:
                    estimated_occ = p_occ
                else:
                    occ = occurrence_gen.next()
                    continue
            else:
                # if there is no persistent match, use the original occ
                estimated_occ = occ

            if any(additional_occs) and (
                    estimated_occ.start == additional_occs[0].start):
                final_occ = additional_occs.pop(0)
            else:
                final_occ = estimated_occ
            if not final_occ.cancelled:
                yield final_occ
            occ = occurrence_gen.next()

    def get_rrule_object(self):
        """Returns the rrule object for this ``Event``."""
        if self.rule:
            params = self.rule.get_params()
            frequency = 'rrule.{0}'.format(self.rule.frequency)
            return rrule.rrule(eval(frequency), dtstart=self.start, **params)


class EventCategory(models.Model):
    """The category of an event."""
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
    )

    color = ColorField(
        verbose_name=_('Color'),
    )

    def __unicode__(self):
        return self.name


class EventRelation(models.Model):
    """
    This class allows to relate additional or external data to an event.

    :event: A FK to the ``Event`` this additional data is related to.
    :content_type: A FK to ContentType of the generic object.
    :object_id: The id of the generic object.
    :content_object: The generic foreign key to the generic object.
    :relation_type: A string representing the type of the relation. This allows
        to relate to the same content_type several times but mean different
        things, such as (normal_guests, speakers, keynote_speakers, all being
        Guest instances)

    """

    event = models.ForeignKey(
        'Event',
        verbose_name=_("Event"),
    )

    content_type = models.ForeignKey(
        ContentType,
    )

    object_id = models.IntegerField()

    content_object = generic.GenericForeignKey(
        'content_type',
        'object_id',
    )

    relation_type = models.CharField(
        verbose_name=_('Relation type'),
        max_length=32,
        blank=True, null=True,
    )

    def __unicode__(self):
        return 'type "{0}" for "{1}"'.format(
            self.relation_type, self.event.title)


class Occurrence(EventModelMixin):
    """
    Needed if one occurrence of an event has slightly different settings than
    all other.

    :created_by: FK to the ``User``, who created this event.
    :event: FK to the ``Event`` this ``Occurrence`` belongs to.
    :original_start: The original start of the related ``Event``.
    :original_end: The original end of the related ``Event``.
    :title: The title of the event.

    """
    created_by = models.ForeignKey(
        'auth.User',
        verbose_name=_('Created by'),
        related_name='occurrences',
    )

    event = models.ForeignKey(
        'Event',
        verbose_name=_('Event'),
        related_name='occurrences',
    )

    original_start = models.DateTimeField(
        verbose_name=_('Original start'),
    )

    original_end = models.DateTimeField(
        verbose_name=_('Original end'),
    )

    cancelled = models.BooleanField(
        verbose_name=_('Cancelled'),
    )

    title = models.CharField(
        max_length=256,
        verbose_name=_('Title'),
        blank=True,
    )

    def category(self):
        return self.event.category

    def delete_period(self, period):
        """Deletes a set of occurrences based on the given decision."""
        # check if this is the last or only one
        is_last = False
        is_only = False
        gen = self.event.get_occurrences(
            self.start, self.event.end_recurring_period)
        occs = [occ for occ in gen]
        if len(occs) == 1:
            is_only = True
        elif len(occs) > 1 and self == occs[-1]:
            is_last = True
        if period == OCCURRENCE_DECISIONS['all']:
            # delete all persistent occurrences along with the parent event
            self.event.occurrences.all().delete()
            self.event.delete()
        elif period == OCCURRENCE_DECISIONS['this one']:
            # check if it is the last one. If so, shorten the recurring period,
            # otherwise cancel the event
            if is_last:
                self.event.end_recurring_period = self.start - timedelta(
                    days=1)
                self.event.save()
            elif is_only:
                self.event.occurrences.all().delete()
                self.event.delete()
            else:
                self.cancelled = True
                self.save()
        elif period == OCCURRENCE_DECISIONS['following']:
            # just shorten the recurring period
            self.event.end_recurring_period = self.start - timedelta(days=1)
            self.event.occurrences.filter(start__gte=self.start).delete()
            if is_only:
                self.event.delete()
            else:
                self.event.save()


class Rule(models.Model):
    """
    This defines the rule by which an event will recur.

    :name: Name of this rule.
    :description: Description of this rule.
    :frequency: A string representing the frequency of the recurrence.
    :params: JSON string to hold the exact rule parameters as used by
        dateutil.rrule to define the pattern of the recurrence.

    """
    name = models.CharField(
        verbose_name=_("name"),
        max_length=32,
    )

    description = models.TextField(
        _("description"),
    )

    frequency = models.CharField(
        verbose_name=_("frequency"),
        choices=FREQUENCY_CHOICES,
        max_length=10,
    )

    params = models.TextField(
        verbose_name=_("params"),
        blank=True, null=True,
    )

    def __unicode__(self):
        return self.name

    def get_params(self):
        if self.params:
            return json.loads(self.params)
        return {}
