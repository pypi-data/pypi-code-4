# -*- coding: utf-8 -*-
"""Listing Quick Search Portlet."""

# zope imports
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.directives import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.z3cform import z2
from z3c.form import button, field
from z3c.form.browser import checkbox, radio
from z3c.form.interfaces import HIDDEN_MODE, IFormLayer
from zope import formlib, schema
from zope.interface import alsoProvides, implementer
from zope.schema.fieldproperty import FieldProperty

# local imports
from plone.mls.listing.browser import listing_search
from plone.mls.listing.browser.valuerange.widget import ValueRangeFieldWidget
from plone.mls.listing.i18n import _

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False


MSG_PORTLET_DESCRIPTION = _(u'This portlet shows a listing quick search form.')

#: Definition of available fields in the given ``rows``.
FIELD_ORDER = {
    'row_listing_type': [
        'listing_type',
    ],
    'row_location': [
        'location_state',
        'location_county',
        'location_district',
        'location_city',
    ],
    'row_beds_baths': [
        'beds',
        'baths',
    ],
    'row_object_type': [
        'object_type',
    ],
    'row_price': [
        'price_min',
        'price_max',
    ],
    'row_sizes': [
        'lot_size',
        'interior_area',
    ],
    'row_filter': [
        'air_condition',
        'pool',
        'jacuzzi',
        'location_type',
        'geographic_type',
    ],
}


class QuickSearchForm(form.Form):
    """Quick Search Form."""
    fields = field.Fields(listing_search.IListingSearchForm)
    template = ViewPageTemplateFile('templates/search_form.pt')
    ignoreContext = True
    method = 'get'

    fields['listing_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['location_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['object_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['baths'].widgetFactory = ValueRangeFieldWidget
    fields['beds'].widgetFactory = ValueRangeFieldWidget
    fields['lot_size'].widgetFactory = ValueRangeFieldWidget
    fields['interior_area'].widgetFactory = ValueRangeFieldWidget

    # Additional fields for filtering.
    fields['geographic_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['view_type'].widgetFactory = checkbox.CheckBoxFieldWidget
    fields['ownership_type'].widgetFactory = checkbox.CheckBoxFieldWidget

    fields['air_condition'].widgetFactory = radio.RadioFieldWidget
    fields['jacuzzi'].widgetFactory = radio.RadioFieldWidget
    fields['pool'].widgetFactory = radio.RadioFieldWidget

    def __init__(self, context, request, data=None):
        """Customized form constructor.

        This one also takes an optional ``data`` attribute so it can be
        instantiated from within a portlet without loosing access to the
        portlet data.
        """
        super(QuickSearchForm, self).__init__(context, request)
        self.data = data

    def updateWidgets(self):
        super(QuickSearchForm, self).updateWidgets()
        # Temporary hide those 2 fields
        if 'location_county' in self.widgets.keys():
            self.widgets['location_county'].mode = HIDDEN_MODE
        if 'location_district' in self.widgets.keys():
            self.widgets['location_district'].mode = HIDDEN_MODE

    @button.buttonAndHandler(PMF(u'label_search', default=u'Search'),
                             name='search')
    def handle_search(self, action):
        """Search button."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

    @property
    def action(self):
        """See interfaces.IInputForm."""
        p_state = self.context.unrestrictedTraverse("@@plone_portal_state")
        search_path = self.data.target_search
        if search_path.startswith('/'):
            search_path = search_path[1:]
        return '/'.join([p_state.portal_url(), search_path])

    def _widgets(self, row):
        """Return a list of widgets that should be shown for a given row."""
        widget_data = dict(self.widgets.items())
        available_fields = FIELD_ORDER.get(row, [])
        return [widget_data.get(field, None) for field in available_fields]

    @property
    def show_filter(self):
        """Decides if the filter should be shown or not."""
        form = self.request.form
        return listing_search.IListingSearch.providedBy(self.context) and \
            'form.buttons.search' in form.keys()

    def widgets_listing_type(self):
        """Return the widgets for the row ``row_listing_type``."""
        return self._widgets('row_listing_type')

    def widgets_location(self):
        """Return the widgets for the row ``row_location``."""
        return self._widgets('row_location')

    def widgets_beds_baths(self):
        """Return the widgets for the row ``row_beds_baths``."""
        return self._widgets('row_beds_baths')

    def widgets_object_type(self):
        """Return the widgets for the row ``row_object_type``."""
        return self._widgets('row_object_type')

    def widgets_price(self):
        """Return the widgets for the row ``row_price``."""
        return self._widgets('row_price')

    def widgets_sizes(self):
        """Return the widgets for the row ``row_sizes``."""
        return self._widgets('row_sizes')

    def widgets_filter(self):
        """Return the widgets for the row ``row_filter``."""
        return self._widgets('row_filter')

    def widgets_filter_other(self):
        """Return all other widgets that have not been shown until now."""
        defined_fields = FIELD_ORDER.values()
        shown_fields = [shown_field for field_lists in defined_fields for
                        shown_field in field_lists]
        return [widget for field_name, widget in self.widgets.items() if not
                field_name in shown_fields]


class IQuickSearchPortlet(IPortletDataProvider):
    """A portlet displaying a listing quick search form."""

    heading = schema.TextLine(
        description=_(
            u'Custom title for the portlet (search mode). If no title is '
            u'provided, the default title is used.'
        ),
        required=False,
        title=_(u'Portlet Title (Search)'),
    )

    heading_filter = schema.TextLine(
        description=_(
            u'Custom title for the portlet (filter mode). If no title is '
            u'provided, the default title is used.'
        ),
        required=False,
        title=_(u'Portlet Title (Filter)'),
    )

    target_search = schema.Choice(
        description=_(
            u'Find the search page which will be used to show the results.'
        ),
        required=True,
        source=SearchableTextSourceBinder({
            'object_provides': 'plone.mls.listing.browser.listing_search.'
                               'IListingSearch',
        }, default_query='path:'),
        title=_(u'Search Page'),
    )


@implementer(IQuickSearchPortlet)
class Assignment(base.Assignment):
    """Quick Search Portlet Assignment."""

    heading = FieldProperty(IQuickSearchPortlet['heading'])
    heading_filter = FieldProperty(IQuickSearchPortlet['heading_filter'])
    target_search = None

    title = _(u'Search Listings')
    title_filter = _(u'Filter Results')
    mode = 'SEARCH'

    def __init__(self, heading=None, heading_filter=None, target_search=None):
        self.heading = heading
        self.heading_filter = heading_filter
        self.target_search = target_search


class Renderer(base.Renderer):
    """Listing Quick Search Portlet Renderer."""

    @property
    def available(self):
        """Check the portlet availability."""
        search_path = self.data.target_search

        if search_path is None:
            return False

        if search_path.startswith('/'):
            search_path = search_path[1:]

        try:
            search_view = self.context.restrictedTraverse(search_path)
        except Unauthorized:
            return False

        return listing_search.IListingSearch.providedBy(search_view) and \
            self.mode != 'HIDDEN'

    @property
    def title(self):
        """Return the title dependend on the mode that we are in."""
        if self.mode == 'SEARCH':
            if self.data.heading is not None:
                return self.data.heading
            return self.data.title
        if self.mode == 'FILTER':
            if self.data.heading_filter is not None:
                return self.data.heading_filter
            return self.data.title_filter

    @property
    def mode(self):
        """Return the mode that we are in.

        This can be either ``FILTER`` if a search was already performed and we
        are on a search page or ``SEARCH`` otherwise.
        """
        form = self.request.form
        if listing_search.IListingSearch.providedBy(self.context) and \
                'form.buttons.search' in form.keys():
            return 'FILTER'
        elif listing_search.IListingSearch.providedBy(self.context) and \
                not 'form.buttons.search' in form.keys():
            return 'HIDDEN'
        else:
            return 'SEARCH'

    def update(self):
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = QuickSearchForm(aq_inner(self.context), self.request,
                                    self.data)
        if HAS_WRAPPED_FORM:
            alsoProvides(self.form, IWrappedForm)
        self.form.update()


class AddForm(base.AddForm):
    """Add form for the Listing Quick Search portlet."""
    form_fields = formlib.form.Fields(IQuickSearchPortlet)
    form_fields['target_search'].custom_widget = UberSelectionWidget

    label = _(u'Add Listing Quick Search portlet')
    description = MSG_PORTLET_DESCRIPTION

    def create(self, data):
        assignment = Assignment()
        formlib.form.applyChanges(assignment, self.form_fields, data)
        return assignment


class EditForm(base.EditForm):
    """Edit form for the Listing Quick Search portlet."""
    form_fields = formlib.form.Fields(IQuickSearchPortlet)
    form_fields['target_search'].custom_widget = UberSelectionWidget

    label = _(u'Edit Listing Quick Search portlet')
    description = MSG_PORTLET_DESCRIPTION
