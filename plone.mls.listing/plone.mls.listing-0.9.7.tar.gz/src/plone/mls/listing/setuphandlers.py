# -*- coding: utf-8 -*-
"""Setup handlers for plone.mls.listing."""

# zope imports
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getUtility

LISTING_TYPE = 'plone.mls.listing.listing'


def setup_kupu(context):
    """Set up Kupu."""
    if not context.readDataFile('plone.mls.listing_various.txt'):
        return

    site = getUtility(IPloneSiteRoot)

    portal_types = getToolByName(site, 'portal_types')
    kupu = getToolByName(site, 'kupu_library_tool', None)
    if kupu is not None:
        linkable = list(kupu.getPortalTypesForResourceType('linkable'))
        if LISTING_TYPE not in linkable:
            # Kupu's resource list can accumulate old, no longer valid types.
            # It will throw an exception if we try to resave them.
            # So, let's clean the list.
            valid_types = dict([(t.id, 1) for t in \
                                portal_types.listTypeInfo()])
            linkable = [pt for pt in linkable if pt in valid_types]

            linkable.append(LISTING_TYPE)
            kupu.updateResourceTypes(({
                'resource_type': 'linkable',
                'old_type': 'linkable',
                'portal_types': linkable,
            },))


def setup_article(context):
    """Set up raptus.article."""
    if not context.readDataFile('plone.mls.listing_various.txt'):
        return

    site = getUtility(IPloneSiteRoot)
    quickinstaller = getToolByName(site, 'portal_quickinstaller')
    portal_types = getToolByName(site, 'portal_types')
    if quickinstaller.isProductInstalled('raptus.article.core'):
        article = portal_types.get('Article', None)
        if article is None:
            return
        if not LISTING_TYPE in article.allowed_content_types:
            article.allowed_content_types += (LISTING_TYPE, )


def setup_versioning(context):
    """Enable versioning in portal types."""
    if not context.readDataFile('plone.mls.listing_various.txt'):
        return

    try:
        from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES
        # we're on plone < 4.1, configure versionable types manually
    except ImportError:
        # repositorytool.xml will be used
        pass
    else:
        site = getUtility(IPloneSiteRoot)
        portal_repository = getToolByName(site, 'portal_repository')
        versionable = list(portal_repository.getVersionableContentTypes())
        if LISTING_TYPE not in versionable:
            # Use append() to make sure we don't overwrite any content types
            # which may already be under version control.
            versionable.append(LISTING_TYPE)
            # Add default versioning policies to the versioned type.
            for policy_id in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(LISTING_TYPE,
                                                          policy_id)
        portal_repository.setVersionableContentTypes(versionable)
