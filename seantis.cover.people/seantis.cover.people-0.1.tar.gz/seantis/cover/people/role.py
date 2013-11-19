from five import grok

from plone import api
from plone.directives import form
from plone.uuid.interfaces import IUUID
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from z3c.form import button

from collective.cover.content import ICover
from seantis.cover.people import _


class IRole(form.Schema):

    form.mode(tile='hidden')
    tile = schema.TextLine(
        title=u'Tile UUID',
    )

    form.mode(person='hidden')
    person = schema.TextLine(
        title=u'Person UUID',
    )

    role = schema.TextLine(
        title=_(u'Role'),
        required=False
    )


class RoleEditForm(form.SchemaForm):
    """ From to edit the role of a member in an organization. """
    
    grok.name('edit-role')
    grok.require('cmf.ModifyPortalContent')
    grok.context(ICover)

    schema = IRole
    ignoreContext = True

    label = _(u'Edit role')

    @property
    def redirect_url(self):
        return '/'.join((self.context.absolute_url(), 'compose'))

    def update(self, **kwargs):

        super(RoleEditForm, self).update(**kwargs)

        person_uuid = self.request.get('person')
        tile_uuid = self.request.get('tile')

        if not all((person_uuid, tile_uuid)):
            return

        self.label = _(u'Edit role of ${organization} / ${person}', mapping={
            'person': api.content.get(UID=person_uuid).title,
            'organization': self.context.title
        })

        self.widgets['tile'].value = tile_uuid
        self.widgets['person'].value = person_uuid
        self.widgets['role'].value = self.get_role(tile_uuid, person_uuid)

    def tile_data_key(self, tile_uuid):
        return 'plone.tiles.data.{}'.format(tile_uuid)

    def get_role(self, tile_uuid, person_uuid):
        data = IAnnotations(self.context).get(self.tile_data_key(tile_uuid))
        roles = data.get('roles') or {}
        
        return roles.get(person_uuid, u'')

    def set_role(self, tile_uuid, person_uuid, role):
        person = api.content.get(UID=person_uuid)
        key = self.tile_data_key(tile_uuid)

        data = IAnnotations(self.context).get(key)
        data['roles'] = data.get('roles') or {}
        data['roles'][IUUID(person)] = role

        IAnnotations(self.context)[key] = data
        
        # notify both ends as they might rely on the role data
        notify(ObjectModifiedEvent(self.context))
        notify(ObjectModifiedEvent(person))

    @button.buttonAndHandler(_(u'Save'))
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.set_role(data['tile'], data['person'], data['role'])
        self.request.response.redirect(self.redirect_url)

    @button.buttonAndHandler(_(u'Cancel'))
    def handleCancel(self, action):
        self.request.response.redirect(self.redirect_url)
