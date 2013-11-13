#coding=utf8
from .utils import ensure_workflow_state
from .utils import get_workflow_state
from .utils import ofs_file_copy
from .utils import ofs_image_copy
from Products.ATContentTypes.lib import constraintypes
from Products.Archetypes.Field import FileField
from Products.Archetypes.Field import ImageField
from Products.Archetypes.Field import ReferenceField
from Products.Archetypes.Field import TextField
from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from prdg.zope.permissions import add_local_role_to_user
import pickle
import zope.event

__MARKER = object()


def create_obj_from_dict(
    container,
    data,
    default_data={},
    send_notification_event=False,
    fail_if_already_exist=True
):
    """
    Create an object inside `container`, with the data from the `data` dict.

    `data` must have the following keys:
    - portal_type: The type, as in the portal_types tool.
    - id: The ID.

    The following special keys are recognized:
    - sub_objects: Call this function recursively on this sequence of dicts.
    - layout: The view template, i.e. setLayout(layout) will be called.
    - allowed_content_types: A sequence of portal type names.
        Set "constraint types" to enabled and set the allowed types.
    - workflow_transition: Do this workflow transition after create the object.
        E.g: 'publish'.
    - workflow_dest_state: Do a workflow transition to the given state.
        If such a transition does not exists then an error will be raised.
        If the given state is the same as the initial state then nothing
        happens.
    - owner_userid -- ID of the owner of the object. The owner will be changed
        to this user.
    - local_roles -- A mapping from user IDs (or group IDs) to sequences
        of local roles to add on the object.

    Warning: Mixing workflow_transition and workflow_destination_state leads to
    a unknown result. These keys are NOT meant to be used together.

    The remaining keys in the dict must be field names to set in the object.

    Reference fields handling:
    Reference fields can be set in a different way. If the key is prefixed
    with "ref:" then the value is interpreted as a sequence of tuples
    representing paths, relative to the site root. E.g:
    'ref:relatedItems': [('documents', 'doc1'), ('events', 'folder2', 'e2')]

    Note: an item of the data dict is processed even if the key is None. E.g
    if the "someField" key maps to None, then someField will be set to None.
    If you don't want to set any value in the field then simply don't put the
    key in the dict. This note applies for the special keys too.

    `default_data` is dict containing default values. If a key is not found in
    data the it is looked up in default_data.

    If `send_notification_event` is True then send the ObjectInitializedEvent
    to the created object.

    If `fail_if_already_exist` is True then an exception will be raised if an
    object with the same ID already exists in `container`. Otherwise nothing
    will happen and `None` will be returned.

    Return: the created object or `None` if `fail_if_already_exist` is `False`
        and an object with the same ID already exists in `container`.
    """
    ptool = getToolByName(container, 'plone_utils')

    # Create a copy of the dict. We don't want to modify the dict.
    data = dict(data)

    for (k, v) in default_data.iteritems():
        if k not in data:
            data[k] = v

    # Required keys.
    portal_type = data.pop('portal_type')
    oid = data.pop('id')

    if (not fail_if_already_exist) and (oid in container.objectIds()):
        return None

    # Special keys.
    sub_objects = data.pop('sub_objects', [])
    layout = data.pop('layout', __MARKER)
    allowed_content_types = data.pop('allowed_content_types', __MARKER)
    workflow_transition = data.pop('workflow_transition', __MARKER)
    workflow_dest_state = data.pop('workflow_dest_state', __MARKER)
    owner_userid = data.pop('owner_userid', __MARKER)
    local_roles = data.pop('local_roles', __MARKER)

    # Reference fields.
    ref_fields = []
    for k in data:
        parts = k.split(':')
        if (len(parts) == 2) and (parts[0] == 'ref'):
            field_name = parts[1]
            ref_fields.append((field_name, data[k]))

    for (k, v) in ref_fields:
        del data['ref:' + k]

    container.invokeFactory(type_name=portal_type, id=oid, **data)

    obj = getattr(container, oid)

    if layout is not __MARKER:
        obj.setLayout(layout)

    if allowed_content_types is not __MARKER:
        aspect = ISelectableConstrainTypes(obj)
        aspect.setConstrainTypesMode(constraintypes.ENABLED)
        aspect.setImmediatelyAddableTypes(allowed_content_types)
        aspect.setLocallyAllowedTypes(allowed_content_types)

    wftool = getToolByName(container, 'portal_workflow')

    if workflow_transition is not __MARKER:
        wftool.doActionFor(obj, workflow_transition)

    if (workflow_dest_state is not __MARKER):
        ensure_workflow_state(obj, workflow_dest_state)

    if (owner_userid is not __MARKER) and (ptool.getOwnerName(obj) != owner_userid):

        ptool = getToolByName(container, 'plone_utils')

        ptool.changeOwnershipOf(obj, owner_userid)

    if (local_roles is not __MARKER):
        for (user_id, roles) in local_roles.iteritems():
            for role in roles:
                add_local_role_to_user(obj, role, user_id)

    for sub_obj_data in sub_objects:
        create_obj_from_dict(obj, sub_obj_data, default_data)

    for (name, paths) in ref_fields:
        set_reference_field(obj, name, paths)

    if send_notification_event:
        send_object_initialized_event(obj)

    return obj


def create_dict_from_obj(obj):
    """
    Return: a dict corresponding to the given object, suitable for
        create_obj_from_dict(). Sub-objects (i.e contained objects) are not
        added to the dict. Also add the _path key containing the obj path
        relative to the site root as a tuple.
    """
    ptool = getToolByName(obj, 'plone_utils')

    d = {}

    for f in obj.Schema().fields():
        field_name = f.getName()

        # Warning: keep the ImageField test first, because ImageField inherits
        # from FileField.
        # Warning 2: TextField inherits from FileField, but must be handled
        # as a common field.
        if isinstance(f, ImageField):
            field_value = f.get(obj)
            value = field_value and ofs_image_copy(field_value)
        elif isinstance(f, FileField) and (not isinstance(f, TextField)):
            field_value = f.get(obj)
            value = field_value and ofs_file_copy(field_value)
        elif isinstance(f, ReferenceField):
            field_name = 'ref:' + field_name
            refs = f.get(obj, aslist=True)
            value = objs_to_paths(refs)
        else:
            value = f.get(obj)

        d[field_name] = value

    d['portal_type'] = obj.portal_type

    wf_state = get_workflow_state(obj)
    if wf_state:
        d['workflow_dest_state'] = wf_state

    d['owner_userid'] = ptool.getOwnerName(obj)
    d['_path'] = obj.getPhysicalPath()[2:]
    local_roles = getattr(obj, '__ac_local_roles__', None)
    if local_roles is not None:
        d['local_roles'] = dict(local_roles)

    # Make sure d is pickable.
    try:
        pickle.dumps(d)
    except:
        obj.plone_log(d)
        raise

    return d


def create_dict_for_all_objs(portal, query={}):
    """
    Iterate through all objects in portal catalog, yielding
    create_dict_from_obj(obj) for each one. The yielded dicts are ordered
    by path. In other words, a parent object is always yielded before its
    children.

    Arguments:
    query -- Optionally filter the results using this catalog query.
    """
    catalog = getToolByName(portal, 'portal_catalog')
    brains = catalog.searchResults(query)
    brains = sorted(brains, key=lambda b: b.getPath())

    for b in brains:
        yield create_dict_from_obj(b.getObject())


def paths_to_objs(context, paths):
    """
    Arguments:
    paths -- An iterable of tuples representing paths relative to the site
        root. Eg.: [('events', 'event1'), ('Documents', 'doc2')].

    Return:
    A sequence of objects corresponding to the given paths.
    """
    utool = getToolByName(context, 'portal_url')
    portal = utool.getPortalObject()

    return [portal.unrestrictedTraverse('/'.join(p)) for p in paths]


def objs_to_paths(objs):
    """The inverse of paths_to_objs()."""
    return [o.getPhysicalPath()[2:] for o in objs]


def set_reference_field(obj, field_name, paths):
    """
    Set a reference field on a given obj.

    Arguments:
    obj -- An object.
    field_name -- The name of the field to be set.
    paths -- An iterable of tuples representing paths relative to the site
        root. Eg.: [('events', 'event1'), ('Documents', 'doc2')].
    """
    obj.getField(field_name).set(obj, paths_to_objs(obj, paths))


def create_folders(context, path):
    """
    Create all folders in a path. Existing folders are not re-created.
    Works like "mkdir -p".

    Arguments:
    context -- Context where to create the folders.
    path -- A tuple representing a path relative to context.

    Return: The folder denoted by the given path.
    """
    for f in path:
        folder = getattr(context, f, None)
        if folder is None:
            context.invokeFactory(type_name='Folder', id=f)
            folder = getattr(context, f)

        context = folder

    return context


def move_objects(from_container, ids, to_container):
    """Move objects from one container to another."""
    cut_data = from_container.manage_cutObjects(ids)
    to_container.manage_pasteObjects(cut_data)


def send_object_initialized_event(obj):
    """Send the `ObjectInitializedEvent` to `obj`."""
    zope.event.notify(ObjectInitializedEvent(obj))


def print_dicts(dicts, out):
    for d in dicts:
        for (k, v) in d.iteritems():
            print >> out, '%s: %s' % (k, v)
        print >> out, 80 * '-'
