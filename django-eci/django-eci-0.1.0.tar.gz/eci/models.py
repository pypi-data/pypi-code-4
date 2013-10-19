from django.db import models

import utils


class Initiative(models.Model):
    STATUS_ONGOING = 'ongoing'
    STATUS_FINALISED = 'finalised'
    STATUS_OBSOLETE = 'obsolete'
    STATUS_NON_REGISTERED = 'non-registered'
    STATUSES = (
        ('ongoing', 'Ongoing'),
        ('finalised', 'Closed'),
        ('obsolete', 'Obsolete'),
        ('non-registered', 'Refused'),
    )

    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    subject = models.TextField(blank=True)
    objectives = models.TextField(blank=True)
    website = models.CharField(max_length=200, blank=True)

    registration_number = models.CharField(max_length=100)
    registration_date = models.DateField()
    deadline = models.DateField()

    data_url = models.CharField(max_length=400)

    status = models.CharField(max_length=20, choices=STATUSES)

    total_signatures = models.IntegerField(null=True, blank=True)
    last_checked_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'eci_initiatives'

    def __unicode__(self):
        return self.title

    def write_current_data(self):
        utils.write_current_data(self)


class Country(models.Model):
    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'eci_countries'
        verbose_name_plural = 'Countries'

    def __unicode__(self):
        return self.name

    @classmethod
    def create_if_needed(cls, code, name):
        _obj, _created = cls.objects.get_or_create(code=code, name=name)


class CountryInitiative(models.Model):
    country = models.ForeignKey(Country, related_name='countries')
    initiative = models.ForeignKey(Initiative, related_name='initiatives')
    threshold = models.IntegerField()

    current_count = models.IntegerField()
    current_percentage = models.DecimalField(max_digits=9, decimal_places=2)
    last_checked_on = models.DateTimeField()

    class Meta:
        db_table = 'eci_countries_initiatives'
        verbose_name_plural = 'Country Initiative'

    def __unicode__(self):
        return u'{} for {}'.format(self.country, self.initiative)


class Signature(models.Model):
    country_initiative = models.ForeignKey(CountryInitiative, related_name='signatures')

    timestamp = models.DateTimeField()
    count = models.IntegerField()
    percentage = models.DecimalField(max_digits=9, decimal_places=2)

    class Meta:
        db_table = 'eci_signatures'
        ordering = ('-timestamp', )

    def __unicode__(self):
        return u'{} has {} new signatures at {}'.format(
            self.country_initiative, self.count, self.timestamp,)
