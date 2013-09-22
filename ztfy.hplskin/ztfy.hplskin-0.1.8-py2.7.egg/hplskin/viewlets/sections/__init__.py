### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = "restructuredtext"

# import standard packages
import random

# import Zope3 interfaces

# import local interfaces
from ztfy.blog.interfaces.section import ISection
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.hplskin.interfaces import IBannerManager

# import Zope3 packages
from zope.component import queryAdapter
from zope.traversing.api import getParents

# import local packages
from ztfy.skin.viewlet import ViewletBase
from ztfy.utils.traversing import getParent


class SectionsViewlet(ViewletBase):

    @property
    def sections(self):
        result = []
        context = None
        parents = getParents(self.context) + [self.context, ]
        sections = [s for s in getParents(self.context) if ISection.providedBy(s)]
        if sections:
            context = sections[-1]
        elif ISection.providedBy(self.context):
            context = self.context
        if context is not None:
            for section in (s for s in context.sections if s.visible):
                selected = section in parents
                subsections = ()
                if selected and ISection.providedBy(section):
                    subsections = [s for s in section.sections if s.visible]
                    if not subsections:
                        subsections = [t for t in section.getVisibleTopics()]
                        if len(subsections) == 1:
                            subsections = []
                result.append({ 'section': section,
                                'selected': selected,
                                'subsections': subsections,
                                'subselected': set(subsections) & set(parents) })
        return result

    @property
    def banner(self):
        site = getParent(self.context, ISiteManager)
        banner = queryAdapter(site, IBannerManager, 'left')
        if banner:
            return random.choice(banner.values())
        return None
