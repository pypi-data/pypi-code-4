from collections import OrderedDict

from django.db import models
from django.utils.translation import ugettext_lazy, ugettext as _

import django_countries
import jsonfield.fields
from model_utils.managers import PassThroughManager

class PublicHolidayQuerySet(models.query.QuerySet):
    def after(self, date):
        return self.filter(date__gte=date)
    
    def between(self, start, finish):
        return self.filter(date__gte=start, date__lte=finish)
    
    def for_country(self, country, province=None):
        if getattr(country, 'code', None):
            country = country.code
        
        qs = self.filter(country=country)
        if province:
            qs = qs.filter(models.Q(provinces=None) | models.Q(provinces=[]) | models.Q(provinces__contains=province))
        return qs
    
    def on(self, date):
        if self.filter(date=date).exists():
            return self.filter(date=date)
    
    def as_json(self):
        data = OrderedDict()
        for holiday in self.order_by('date'):
            date = holiday.date.strftime('%Y-%m-%d')
            if date not in data:
                data[date] = []
            data[date].append({
                'name': holiday.name,
                'country': {
                    'code': holiday.country.code, 
                    'name': unicode(holiday.country.name)
                },
                'provinces': holiday.provinces
            })
        
        return data
    
class PublicHoliday(models.Model):
    """
    A PublicHoliday is an object that can be associated with a country, and
    zero or more provinces. The semantic meaning of no listed provinces is
    that the PublicHoliday is nationwide.
    
    The provinces list should be CSV list of provinces from the django
    localflavor module.
    
    This is a seperate app, that relies on django-countries, with my
    province patches applied, and django-jsonfield.
    """
    
    #: Every PublicHoliday must have a name.
    name = models.CharField(max_length=128)
    #: PublicHolidays are single-day events, and do not automatically repeat.
    date = models.DateField()
    #: Each PublicHoliday can only apply to one country.
    country = django_countries.CountryField()
    #: Each PublicHoliday can apply to all, or a subset of provinces in
    #: a country.
    provinces = jsonfield.fields.JSONField(null=True, blank=True,
        help_text=_(u'No selected provinces means that all provinces are affected.'))
    
    objects = PassThroughManager.for_queryset_class(PublicHolidayQuerySet)()
    
    class Meta:
        app_label = 'public_holidays'
        verbose_name = u'public holiday'
        verbose_name_plural = u'public holidays'
        ordering = ('date', 'country')
        unique_together = (
            ('name', 'date', 'country'),
        )
    
    def __init__(self, *args, **kwargs):
        super(PublicHoliday, self).__init__(*args, **kwargs)
        # Fixups for bad data stored in provinces field.
        if self.provinces:
            self.provinces = sorted(self.provinces)
            if '' in self.provinces:
                self.provinces.remove('')
            provinces = sorted([x['code'] for x in self.country.provinces])
            if provinces == self.provinces:
                self.provinces = None
        
    def __unicode__(self):
        return "%s (%s) [%s]" % (self.name, self.date.year, self.country)


def public_holiday_on(date, country, province):
    return PublicHoliday.objects.for_country(country, province).on(date)