# -*- coding: utf-8 -*-
"""Various browser views for listings."""

# zope imports
from Products.Five import BrowserView
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from zope.component import getUtility, queryMultiAdapter
from zope.interface import implements

# local imports
from plone.mls.core.interfaces import IMLSSettings
from plone.mls.listing.api import listing_details
from plone.mls.listing.browser.interfaces import IListingDetails
from plone.mls.listing.interfaces import IMLSAgencyContactInformation


class ListingDetails(BrowserView):
    implements(IListingDetails)

    _error = {}
    _data = None
    listing_id = None

    def __init__(self, context, request):
        super(ListingDetails, self).__init__(context, request)
        self.update()

    def update(self):
        self.portal_state = queryMultiAdapter((self.context, self.request),
                                              name='plone_portal_state')
        self._get_data()

    @memoize
    def _get_data(self):
        """Get the remote listing data from the MLS."""
        lang = self.portal_state.language()
        if getattr(self.request, 'listing_id', None) is not None:
            self.listing_id = self.request.listing_id
        else:
            self.listing_id = getattr(self.context, 'listing_id', None)
        if self.listing_id:
            self._data = listing_details(self.listing_id, lang)

    @property
    def data(self):
        return self._data

    @property
    def error(self):
        return self._error

    @property
    def title(self):
        if getattr(self.request, 'listing_id', None) is not None:
            if self.info is not None:
                title = self.info.get('title', None)
                if title is not None:
                    return title.get('value', self.context.title)
        else:
            return self.context.Title

    @property
    def description(self):
        if self.data is not None:
            return self.data.get('description', None)

    @property
    def agent_quote(self):
        if self.data is not None:
            return self.data.get('agent_quote', None)

    @property
    def long_description(self):
        if self.data is not None:
            return self.data.get('long_description', None)

    @property
    def groups(self):
        if self.data is not None:
            return self.data.get('groups', None)

    @property
    def info(self):
        if self.data is not None:
            return self.data.get('info', None)

    @property
    def lead_image(self):
        if self.data is not None:
            image = self.data.get('images', None)[:1]
            if len(image) > 0:
                return image[0]
        return None

    @property
    def images(self):
        if self.data is not None:
            images = self.data.get('images', None)
            if len(images) > 1:
                return images

    @property
    def contact(self):
        registry = getUtility(IRegistry)
        mls_settings = registry.forInterface(IMLSSettings)
        agency_id = getattr(mls_settings, 'agency_id', None)

        if self.data is None:
            return

        contact_data = self.data.get('contact', None)
        agency = contact_data.get('agency', {})
        agent = contact_data.get('agent', {})

        if agency.get('id', {}).get('value', None) == agency_id:
            return contact_data

        settings = registry.forInterface(IMLSAgencyContactInformation)
        if getattr(settings, 'use_custom_info', False) is True:

            # Adjust agency name.
            agency_name = getattr(settings, 'agency_name', None)
            if agency_name is not None:
                item = agency.setdefault('name', {})
                item['value'] = agency_name
            else:
                agency['name'] = None

            # Adjust agency logo.
            agency_logo = getattr(settings, 'agency_logo_url', None)
            if agency_logo is not None:
                agency['logo'] = agency_logo
            else:
                agency['logo'] = None

            # Adjust agency office phone.
            agency_office_phone = \
                getattr(settings, 'agency_office_phone', None)
            if agency_office_phone is not None:
                item = agency.setdefault('office_phone', {})
                item['value'] = agency_office_phone
            else:
                agency['office_phone'] = None

            # Adjust agency website.
            agency_website = getattr(settings, 'agency_website', None)
            if agency_website is not None:
                item = agency.setdefault('website', {})
                item['value'] = agency_website
            else:
                agency['website'] = None

            # Adjust agent name.
            agent_name = getattr(settings, 'agent_name', None)
            if agent_name is not None:
                item = agent.setdefault('name', {})
                item['value'] = agent_name
            else:
                agent['name'] = None

            # Adjust agent title.
            agent_title = getattr(settings, 'agent_title', None)
            if agent_title is not None:
                item = agent.setdefault('title', {})
                item['value'] = agent_title
            else:
                agent['title'] = None

            # Adjust agent office phone.
            agent_office_phone = getattr(settings, 'agent_office_phone', None)
            if agent_office_phone is not None:
                item = agent.setdefault('agent_office_phone', {})
                item['value'] = agent_office_phone
            else:
                agent['agent_office_phone'] = None

            # Adjust agent cell phone.
            agent_cell_phone = getattr(settings, 'agent_cell_phone', None)
            if agent_cell_phone is not None:
                item = agent.setdefault('agent_cell_phone', {})
                item['value'] = agent_cell_phone
            else:
                agent['agent_cell_phone'] = None

            # Adjust agent fax.
            agent_fax = getattr(settings, 'agent_fax', None)
            if agent_fax is not None:
                item = agent.setdefault('agent_fax', {})
                item['value'] = agent_fax
            else:
                agent['agent_fax'] = None

            # Adjust agent email.
            agent_email = getattr(settings, 'agent_email', None)
            if agent_email is not None:
                item = agent.setdefault('agent_email', {})
                item['value'] = agent_email
            else:
                agent['agent_email'] = None

            # TODO: Adjust agent languages.
            # TODO: Adjust agent avatar.

        return contact_data
