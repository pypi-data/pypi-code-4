from zope.interface import Interface, Attribute
from zope.schema import List, Object, Set, TextLine, Text, InterfaceField


class ISubtyped(Interface):
    """An object that has been subtyped with this machinery should provide
    this interface.
    """


class IContentTypeDescriptor(Interface):
    """A descriptor representing information about a content type.
    """

    title = TextLine(title=u'Title')
    description = Text(title=u'Description')
    type_interface = InterfaceField(title=u'Type Interface')


class IFolderishContentTypeDescriptor(IContentTypeDescriptor):
    """A descriptor which allows to describe what possible objects of
    what particular portal_type's can be added as child items.
    """

    allowed_child_portal_types = Set( \
        title=u'Allowed Child Portal Types')


class _IPortalTypedMixin(IContentTypeDescriptor):
    """A set of common fields to use for any descriptor which supports
    discrimination by portal_type.
    """

    for_portal_type = TextLine(title=u'For Portal Type')


class IPortalTypedDescriptor(IContentTypeDescriptor,
                             _IPortalTypedMixin):
    """A descriptor which can be discriminated by portal_type.
    """


class IPortalTypedFolderishDescriptor(IFolderishContentTypeDescriptor,
                                      _IPortalTypedMixin):
    """A folderish descriptor which can be discriminated by portal_type.
    """


class IPossibleDescriptors(Interface):
    """A method of getting the possible descriptors on a given context.
    Intended to be implemented by adapters.
    """

    possible = List( \
        title=u'Possible',
        value_type=Object(title=u'Possible',
                                      schema=IContentTypeDescriptor))


class IPortalTypedPossibleDescriptors(IPossibleDescriptors):
    """A method of getting the possible descriptors on a given context,
    for a given portal_type.
    Intended to be implemented by adapters.
    """


class ISubtyper(Interface):
    """The actual subtyping engine.
    """

    def possible_types(obj):
        """All possible types for a given object.  Will return an iterable
        of objects implementing IContentTypeDescriptor.
        """

    def change_type(obj, descriptor_name):
        """Will change the sub type of the given object to the specified
        type.  If no sub type was already set on the object, the target type
        will be added.  If a sub type already exists, it will be removed
        and the target type will be added.
        """

    def remove_type(obj):
        """Remove any sub type on the object.
        """

    def existing_type(obj):
        """Return the existing type of an object.
        """

    def get_named_type(name):
        """Return descriptor represented by name.
        """


class ISubtypeEvent(Interface):
    object = Attribute('The subject of the event')
    subtype = InterfaceField(title=u'Type Interface')


class ISubtypeAddedEvent(ISubtypeEvent):
    """Fired when a subtype was added to an object.
    """


class ISubtypeRemovedEvent(ISubtypeEvent):
    """Fired when a subtype was removed from an object.
    """


class IDescriptorWithName(Interface):
    """A simple way to match a descriptor with it's registered name.
    """

    name = TextLine(title=u'Name')
    descriptor = Object(title=u'Descriptor', schema=IContentTypeDescriptor)
