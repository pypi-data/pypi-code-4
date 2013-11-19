from collective.cover import _
from collective.cover.tiles.base import IPersistentCoverTile
from collective.cover.tiles.list import ListTile

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.tiles.interfaces import ITileDataManager
from plone import api

from zope import schema
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from seantis.plonetools import tools
from seantis.people.interfaces import IPerson


def get_list_tile_ids( cover):
        for key, values in IAnnotations(cover).items():
            if 'is_memberlist_tile' in values:
                yield key.replace('plone.tiles.data.', '')


def get_list_tiles(cover):
    for uid in get_list_tile_ids(cover):
        path = str('/'.join(('seantis.cover.people.memberlist', uid)))
        yield cover.restrictedTraverse(path)


class IMemberListTile(IPersistentCoverTile):

    uuids = schema.List(
        title=_(u'Members'),
        value_type=schema.TextLine(),
        required=False
    )

    is_memberlist_tile = schema.Bool(
        required=False
    )

    roles = schema.Dict(
        title=_(u'Roles'),
        key_type=schema.TextLine(),
        value_type=schema.TextLine()
    )

class MemberListTile(ListTile):

    implements(IPersistentCoverTile)
    index = ViewPageTemplateFile('templates/list.pt')

    is_editable = False
    is_configurable = True

    short_name = _(u'Memberlist')
    limit = 1000

    def get_role(self, uuid):
        roles = self.data.get('roles') or {}
        return roles.get(uuid, u'')

    def set_role(self, uuid, role):
        data_mgr = ITileDataManager(self)
        data = data_mgr.get()
        data['roles'] = data.get('roles') or {}
        data['roles'][uuid] = role
        data_mgr.set(data)

    def populate_with_object(self, obj):
        super(MemberListTile, self).populate_with_object(obj)
        notify(ObjectModifiedEvent(obj))

    def remove_item(self, uuid):
        super(MemberListTile, self).remove_item(uuid)

        data_mgr = ITileDataManager(self)
        data = data_mgr.get()

        if uuid in data['roles']:
            del data['roles'][uuid]

        data_mgr.set(data)

        notify(ObjectModifiedEvent(api.content.get(UID=uuid)))

    def accepted_ct(self):
        return [
            fti.id for fti in
            tools.get_type_info_by_behavior(IPerson.__identifier__)
        ]
