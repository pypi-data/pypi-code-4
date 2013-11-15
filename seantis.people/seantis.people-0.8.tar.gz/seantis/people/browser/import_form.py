import transaction
from copy import copy
from five import grok

from zope import schema
from z3c.form import field
from z3c.form.button import buttonAndHandler
from plone.directives import form
from plone.namedfile.field import NamedFile

from seantis.people import _
from seantis.people.errors import ContentImportError
from seantis.people.interfaces import IList
from seantis.people.browser import BaseForm
from seantis.people.content.import_content import (
    supported_formats,
    import_people
)

from zope.schema.vocabulary import SimpleVocabulary


class IImportFormSchema(form.Schema):

    portal_type = schema.Choice(title=_(u"Type"), values=[])
    import_file = NamedFile(title=_(u"File"))


class ImportForm(BaseForm):

    label = _(u'Import people')

    permission = 'cmf.ManagePortal'
    grok.require(permission)
    grok.context(IList)
    grok.name('import')

    ignoreContext = True

    template = grok.PageTemplateFile('templates/import_form.pt')

    @property
    def fields(self):
        fields = field.Fields(IImportFormSchema)

        for f in fields.values():
            f.field = copy(f.field)

        fields['portal_type'].field.vocabulary = SimpleVocabulary.fromItems(
            (fti.title, fti.id) for fti in self.context.available_types()
        )

        return fields

    def get_format_from_filename(self, filename):
        if not '.' in filename:
            return ''
        else:
            return filename.split('.')[-1]

    @buttonAndHandler(_(u'Import'), name='import')
    def run_import(self, action):

        if not self.parameters:
            return

        try:
            portal_type = self.parameters['portal_type']
            import_file = self.parameters['import_file']

            format = self.get_format_from_filename(import_file.filename)

            if not format in supported_formats:
                raise ContentImportError(_(
                    u'${format} is not supported, supported are ${formats}',
                    mapping={
                        'format': format,
                        'formats': ', '.join(supported_formats)
                    }
                ))

            count = import_people(
                self.request,
                self.context,
                portal_type,
                format,
                import_file.data
            )

            self.status = _(
                u'Successfully imported ${count} records', mapping=dict(
                    count=count
                )
            )

        except ContentImportError, e:
            transaction.abort()
            self.raise_action_error(e.translate(self.request))

    @buttonAndHandler(_(u'Cancel'), name='cancel')
    def cancel(self, action):
        self.request.response.redirect(self.context.absolute_url())
