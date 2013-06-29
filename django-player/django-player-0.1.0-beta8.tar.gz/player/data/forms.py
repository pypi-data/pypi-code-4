from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.conf import settings
from django.contrib import messages
from django.contrib.formtools.wizard import FormWizard
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.forms.util import ErrorList
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _

from player.base.forms import BaseForm
from player.crawler import get_backend, get_backends
from player.crawler.models import CrawlerCollection
from player.data.models import CollectionGroup, Collection, CollectionField


# ----- collectiongroup form -----


class CollectionGroupForm(BaseForm, forms.ModelForm):

    class Meta:
        model = CollectionGroup


# ----- collection form -----


class CollectionFieldForm(BaseForm, forms.ModelForm):

    class Meta:
        model = CollectionField
        exclude = ('collection', 'mapped_field', 'custom_format', )


class FieldCollectionFormSet(BaseInlineFormSet):

    def clean(self):
        cleaned_data = super(FieldCollectionFormSet, self).clean()
        slug_dict = {}
        c_data = getattr(self, 'cleaned_data', [{}])
        for i, data in enumerate(c_data):
            slug = data.get('slug', None)
            if not slug:
                continue
            if slug in slug_dict:
                slug_errors = self.forms[i]._errors.get('slug', ErrorList([]))
                slug_errors.extend(ErrorList([_(u'Please set other slug. This slug has been assigned')]))
                self.forms[i]._errors['slug'] = ErrorList(slug_errors)
            slug_dict[data['slug']] = data['slug']
        return cleaned_data


class CollectionForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Collection
        exclude = ('last_crawling_time', 'crawler_collection', 'status',
                   'repr_field', 'check_deleted',
                   'new_elements_threshold', 'modified_elements_threshold',
                   'deleted_elements_threshold', 'crawling_checked')

    def __init__(self, *args, **kwargs):
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.fields['collectiongroup'].required = True
        if self.instance:
            self.edit = True
        Formset = inlineformset_factory(parent_model=self._meta.model,
                                      model=CollectionFieldForm._meta.model,
                                      form=CollectionFieldForm,
                                      formset=FieldCollectionFormSet,
                                      extra=1,
                                      can_delete=self.edit)
        self.field_formset = Formset(data=self.data or None,
                                     files=self.files or None,
                                     instance=self.instance)

    def is_valid(self):
        form_valid = super(CollectionForm, self).is_valid()
        formset_valid = self.field_formset.is_valid()
        return form_valid and formset_valid

    def save(self, *args, **kwargs):
        # Clean items and crawler mapping when editing
        if self.edit:
            self.instance.crawler_collection = None
            self.instance.item_set.with_invalids().delete()
            for field in self.instance.fields.all():
                field.mapped_field = None
                field.save()
        return super(CollectionForm, self).save(*args, **kwargs)


# ----- scrap association wizar -----


class FormWithCollection(object):

    def set_collection_and_backend(self, collection, collection_code, backend):
        self.collection = collection
        self.collection_code = collection_code
        self.backend = backend


class SelectBackendFormStep(BaseForm, FormWithCollection, forms.Form):
    backend = forms.ChoiceField(label=_('Backend'))

    def __init__(self, *args, **kwargs):
        super(SelectBackendFormStep, self).__init__(*args, **kwargs)
        self.fields['backend'].choices = (('', '---------'), ) + get_backends()


class CollectionCodeFormStep(BaseForm, FormWithCollection, forms.Form):
    collection_code = forms.CharField(label=_('Collection code'))

    def __init__(self, *args, **kwargs):
        super(CollectionCodeFormStep, self).__init__(*args, **kwargs)

    def set_collection_and_backend(self, collection, collection_code, backend):
        collection_codes = get_backend(backend).get_collection_codes(
            settings.CRAWLER_LOGIN, settings.CRAWLER_PASSWORD,
        )
        if collection_codes is not None:
            self.fields['collection_code'] = forms.ChoiceField(label=_('Collection code'))
            self.fields['collection_code'].choices = (('', '---------'), ) + tuple(collection_codes)


class FieldMappingFormStep(BaseForm, FormWithCollection, forms.Form):

    def set_collection_and_backend(self, collection, collection_code, backend):
        self.collection = collection
        crawler_collection, created = CrawlerCollection.objects.get_or_create(
            collection_code=collection_code, backend=backend,
        )
        if crawler_collection.schema is None:
            get_backend(crawler_collection.backend).load_collection_schema(crawler_collection)
        schema = crawler_collection.schema
        choices = [('', '---------'), ]
        choices += [(key, key) for key, value in schema.items() \
                    if not hasattr(value, 'is_system') or value['is_system'] == 'False']
        for field in collection.fields.all():
            self.fields.update({field.slug: forms.ChoiceField(choices=choices)})
            if field.field_type == 'date':
                help_text = ugettext('By default is %d/%m/%Y. Look at \
<a target="_blank" href="http://docs.python.org/library/datetime.html#strftime-strptime-behavior">date formats page</a> to get more info')
                self.fields.update(
                    {'%s_custom_format' % field.slug: forms.CharField(help_text=help_text)},
                )

    def save(self):
        for key, value in self.cleaned_data.items():
            slug = key.replace('_custom_format', '')
            field = CollectionField.objects.get(collection=self.collection,
                                                slug=slug)
            if key.endswith('_custom_format'):
                field.custom_format = value
            else:
                field.mapped_field = value
            field.save()


class ExtractionParamsFormStep(BaseForm, FormWithCollection, forms.ModelForm):

    class Meta:
        model = CrawlerCollection
        exclude = ('collection_code', 'backend', 'schema', 'last_crawling_time', 'last_job_time')

    def __init__(self, *args, **kwargs):
        super(ExtractionParamsFormStep, self).__init__(*args, **kwargs)

    def set_collection_and_backend(self, collection, collection_code, backend):
        self.instance, created = CrawlerCollection.objects.get_or_create(
            collection_code=collection_code,
        )
        if not created:
            self.initial['check_deleted'] = self.instance.check_deleted
            self.initial['new_elements_threshold'] = self.instance.new_elements_threshold
            self.initial['modified_elements_threshold'] = self.instance.modified_elements_threshold
            self.initial['deleted_elements_threshold'] = self.instance.deleted_elements_threshold


class DeleteItemsFormStep(BaseForm, FormWithCollection, forms.Form):

    crawl = forms.BooleanField(label=ugettext('Launch crawler when finish'), required=False)

    def set_collection_and_backend(self, collection, collection_code, backend):
        self.collection = collection
        self.backend = backend

    def save(self):
        for item in self.collection.item_set.with_invalids():
            item.delete()


class ScrapAssociationWizard(FormWizard):

    def __init__(self, *args, **kwargs):
        self.collection = kwargs.pop('collection', None)
        self.collection_code = None
        self.backend = None
        super(ScrapAssociationWizard, self).__init__(*args, **kwargs)
        self.extra_context = {'collection': self.collection}

    def get_form(self, step, data=None):
        form = super(ScrapAssociationWizard, self).get_form(step, data)
        form.set_collection_and_backend(self.collection, self.collection_code, self.backend)
        return form

    def process_step(self, request, form, step):
        if step == 0:
            if form.is_valid():
                self.backend = form.cleaned_data['backend']
                self.extra_context['backend'] = self.backend
        if step == 1:
            if form.is_valid():
                self.collection_code = form.cleaned_data['collection_code']
                self.extra_context['collection_code'] = self.collection_code

    def get_template(self, step):
        if step == 2:
            return 'data/fieldmappingform_step.html'
        elif step == 3:
            return 'data/thresholdform_step.html'
        elif step == 4:
            return 'data/deleteitemsform_step.html'
        return 'data/data_wizard.html'

    def done(self, request, form_list):
        deleteitemsform = None
        if len(form_list) == 5:
            deleteitemsform = form_list[4]
            deleteitemsform.save()
        collectionfieldmap_form = form_list[2]
        collectionthreshold_form = form_list[3]

        # Save thresholds
        crawler_collection = collectionthreshold_form.save()

        self.collection.crawler_collection = crawler_collection
        self.collection.save()

        # Save mappings
        collectionfieldmap_form.save()
        messages.success(request, ugettext('Scrap associated successfully'))

        if deleteitemsform and deleteitemsform.cleaned_data.get('crawl', False):
            return HttpResponseRedirect(reverse('collection_crawl', args=(self.collection.collectiongroup.slug, self.collection.slug)))
        return HttpResponseRedirect(self.collection.get_absolute_url())
