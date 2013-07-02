import zope.component.interfaces
import zope.event
import zope.interface


class IComponentEvent(zope.component.interfaces.IObjectEvent):
    """ An event about a component of an article
    """
    component = zope.interface.Attribute('The related component')


class IComponentActivatedEvent(IComponentEvent):
    """ An event notified on component activation
    """


class IComponentDeactivatedEvent(IComponentEvent):
    """ An event notified on component deactivation
    """


class ComponentEvent(zope.component.interfaces.ObjectEvent):
    """ An event about a component of an article
    """
    zope.interface.implements(IComponentEvent)

    def __init__(self, object, component):
        super(ComponentEvent, self).__init__(object)
        self.component = component


class ComponentActivatedEvent(ComponentEvent):
    """ An event notified on component activation
    """
    zope.interface.implements(IComponentActivatedEvent)


class ComponentDeactivatedEvent(ComponentEvent):
    """ An event notified on component deactivation
    """
    zope.interface.implements(IComponentDeactivatedEvent)


class Component(object):
    """ A component
    """


@zope.component.adapter(IComponentEvent)
def componentEventNotify(event):
    """Event subscriber to dispatch ComponentEvents to interested adapters."""
    component = Component()
    zope.interface.alsoProvides(component, event.component)
    zope.component.subscribers((event.object, component, event), None)
