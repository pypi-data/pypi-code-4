from collective.cart.core import _
from collective.cart.core.interfaces import IOrderContainer
from collective.cart.core.interfaces import IShoppingSite
from z3c.form.validator import SimpleFieldValidator
from z3c.form.validator import WidgetValidatorDiscriminators
from zope.interface import Invalid


class ValidateOrderIDUniqueness(SimpleFieldValidator):
    """Validate uniqueness of  next order ID of the order container."""

    def validate(self, value):
        super(ValidateOrderIDUniqueness, self).validate(value)

        if value is not None:
            brains = IShoppingSite(self.context).get_brains(depth=1, id=str(value))
            if brains:
                raise Invalid(_(u'order-id-already-in-use', default=u'The order ID is already in use.'))


WidgetValidatorDiscriminators(ValidateOrderIDUniqueness, field=IOrderContainer['next_order_id'])
