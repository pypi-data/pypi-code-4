from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.statusmessages.interfaces import IStatusMessage
from collective.cart.core import _
from collective.cart.core.interfaces import IOrderContainer
from collective.cart.core.interfaces import IMakeShoppingSiteEvent
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from plone.dexterity.utils import createContentInContainer
from zope.component import adapter
from zope.interface import noLongerProvides
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


@adapter(IOrderContainer, IObjectRemovedEvent)
def unmake_shopping_site(container, event):
    if container == event.object:
        parent = aq_parent(aq_inner(container))
        noLongerProvides(parent, IShoppingSiteRoot)
        parent.reindexObject(idxs=['object_provides'])
        message = _(u"This container is no longer a shopping site.")
        IStatusMessage(container.REQUEST).addStatusMessage(message, type='warn')


@adapter(IMakeShoppingSiteEvent)
def add_order_container(event):
    context = event.context
    if not IShoppingSite(context).order_container():
        container = createContentInContainer(
            context, 'collective.cart.core.OrderContainer',
            id="order-container", title="Order Container", checkConstraints=False)
        modified(container)
