# -*- encoding: utf-8 -*-
import json
import random
import string
import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError, FieldError, ObjectDoesNotExist
from django.db import models
from django.db.models import permalink
from django.template.base import Variable, VariableDoesNotExist, Template
from django.template.context import Context
from guardian.models import GroupObjectPermission
from pasportng.ereports import postprocessor
from pasportng.ereports.postprocessor import PostProcessor
from pasportng.ereports.exceptions import OrderDefinitionError, FilterDefinitionError, GroupDefinitionError
from pasportng.pasport.utils.date import last_of_month
from .templatetags.ereports import _get_field, header


clean_field = lambda field: field.replace('.', '__').strip()
keygen = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(100))


class ReportGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    class Meta:
        app_label = 'ereports'

    def __unicode__(self):
        return self.name


class ReportTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    body = models.TextField()
    system = models.BooleanField(default=False)

    class Meta:
        app_label = 'ereports'

    def __unicode__(self):
        return self.name


class Report(models.Model):
    name = models.CharField(max_length=100, unique=True)
    group = models.ForeignKey(ReportGroup)
    template = models.ForeignKey(ReportTemplate, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    target_model = models.ForeignKey(ContentType)
    datasource = models.CharField('PostProcessor', max_length=200, blank=True, null=True, choices=[(k, k) for k, v in postprocessor.registry.iteritems()])

    published = models.BooleanField(default=False)
    select_related = models.BooleanField(default=False)
    use_distinct = models.BooleanField(default=False)

    columns = models.TextField(default='id\n')
    filtering = models.TextField(blank=True, null=True, default="office={{selected_office}}")
    ordering = models.TextField(blank=True, null=True)
    groupby = models.TextField(blank=True, null=True)
    extras = models.TextField(blank=True, null=True)
    rawsql = models.TextField(blank=True, null=True)

    ttl = models.IntegerField('Cache validity (minutes)', default=0)
    cache_key = models.CharField('Cache entry seed', max_length=200, null=False, unique=True, default=keygen)

    class Meta:
        permissions = (('run_report', 'Can run a report'),)
        app_label = 'ereports'

    def __unicode__(self):
        return self.name

    @permalink
    def get_absolute_url(self):
        return 'reports2.do_report', [self.pk]

    def save(self, force_insert=False, force_update=False, using=None):
        if self.cache_key is None:
            self.cache_key = '{0.pk} {0.name} {0.filtering}'.format(self)
        super(Report, self).save(force_insert, force_update, using)

    def get_extra(self, key, default=None):
        if not hasattr(self, '_extras'):
            try:
                self._extras = json.loads(self.extras)
            except ValueError:
                self._extras = {}

        return self._extras.get(key, default)

    def get_target_queryset(self, *args, **context):
        Datasource = postprocessor.registry.get(self.datasource, PostProcessor)
        try:
            model = self.target_model.model_class()

            manager_method_name = self.get_extra('manager', 'filter')
            manager_method = getattr(model.objects, manager_method_name, model.objects.filter)

            filters = self.get_target_filtering(*args, **context)
            order = self.get_target_ordering(*args, **context)

            qs = manager_method(**filters).order_by(*order)

            if self.select_related:
                return qs.select_related()
            qs = Datasource(qs.model, qs.query, None, report=self, queryset=qs)
            return qs
        except FieldError as e:
            raise ValidationError(e)
        except ValidationError as e:
            raise e

    # noinspection PyUnusedLocal
    def get_target_ordering(self, *args, **kwargs):
        try:
            order = []
            for line in self.ordering.split('\n'):
                if line.strip():
                    order.append(line.strip().replace('.', '__'))
            return order
        except Exception as e:
            raise OrderDefinitionError(e)

    def _process_value(self, value_string, context):
        if value_string.startswith('{%'):
            # context['current_row'] = obj
            # HACK!!  todo: find a better way to do that
            pattern = "{%% load ereports %%}%s" % value_string
            t = Template(pattern)
            value = t.render(Context(context))
            if value != u'None':
                return value
        elif value_string.startswith('{{'):
            target = Variable(value_string[2:-2].strip())
            try:
                return target.resolve(Context(context))
            except VariableDoesNotExist:
                return None
        else:
            return value_string

    # noinspection PyUnusedLocal
    def get_target_filtering(self, *args, **kwargs):
        filters = {}
        line = None
        try:
            if self.filtering:
                for line in self.filtering.split('\r\n'):
                    if line.strip():
                        field, value = line.split('=', 2)
                        if field[-1] in '<>':
                            pass
                        v = self._process_value(value, kwargs)
                        if v:
                            filters[clean_field(field)] = v
            return filters
        except Exception as e:
            if line is not None:
                raise FilterDefinitionError("Error on line:`%s` %s" % (line, str(e)))
            raise FilterDefinitionError(e)

    # noinspection PyUnusedLocal
    def get_target_grouping(self, *args, **kwargs):
        groups = []
        line = None
        try:
            if self.groupby:
                for line in self.groupby.split('\r\n'):
                    groups.append(line)
            return groups
        except Exception as e:
            if line is not None:
                raise GroupDefinitionError("Error on line:`%s` %s" % (line, str(e)))
            raise GroupDefinitionError(e)

    def get_columns(self):
        model = self.target_model.model_class()
        cols = []
        headers = []
        for col in self.columns.split('\r\n'):
            parts = col.split('#')
            col = parts[0]
            if len(parts) == 1:
                title = header(model, col)
            elif len(parts) == 2:
                title = parts[1]
            if title.strip():
                headers.append(str(title))
            if col.strip():
                cols.append(col)

        return cols, headers

    # TODO check if this being used
    def clean_target_model(self):
        try:
            # TODO check for dead code
            model = self.target_model.model_class()
        except ObjectDoesNotExist as e:
            raise ValidationError('Invalid Target: %s' % e)

    def get_extra_context(self):
        today = datetime.datetime.today()
        last_day_prev_month = last_of_month(today - relativedelta(months=1))
        # TODO check results for prev_month. Is it intented to be full date or just the month value?
        context = {
            'today': today,
            'current_month': today.month,
            'prev_month': today.month - 1,
            'last_day_prev_month': last_day_prev_month,
            'current_year': today.year,
            'prev_year': today.year - 1
        }
        return context

    def __clean(self):
        """
            * validate filter
            * validate order
            * validate queryset
            * validate header
            * get an object by queryset
            * validate fields
        """
        try:
            model = self.target_model.model_class()
        except ObjectDoesNotExist:
            return

        # filtering
        # try:
        #    for field, value in self.get_target_filtering().items():
        #        if not _get_field(model, field):
        #            raise ValidationError('Invalid Filter: `%s` is not a valid field' % field)
        # except  ValueError as e:
        #    raise ValidationError('Invalid filter: %s' % e)
        #    raise ValidationError('Invalid filter: Entries must be in the formar `field=value`')

        # ordering
        line = None
        try:
            for line in self.get_target_ordering():
                if line.startswith('-'):
                    line = line[1:]
                if not _get_field(model, line):
                    raise ValidationError('Invalid ordering: `%s` is not a valid field ' % line)
        except ValueError:
            raise ValidationError('Invalid ordering: `%s`.' % line)

        # columns
        try:
            self.get_columns()
        except Exception as e:
            raise ValidationError('Invalid column: %s' % e)
        ctx = {}
        today = datetime.datetime.today()
        ctx.update({'today': today,
                    'current_month': today.month,
                    'prev_month': today.month - 1})
        try:
            list(self.get_target_queryset(**self.get_extra_context())[1:3])
        except Exception as e:
            raise ValidationError('Cannot create a queryset. Please check your inputs %s' % str(e))


class ReportPermission(GroupObjectPermission):
    class Meta:
        proxy = True
        app_label = 'ereports'
        verbose_name = 'Report Permission'
