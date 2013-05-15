### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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
from ztfy.scheduler.interfaces import ISchedulerTask

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface
from zope.schema import Bool, TextLine, Datetime, Int

# import local packages
from ztfy.security.schema import Principal

from ztfy.sendit import _


#
# User profile info
#

class IProfileInfo(Interface):
    """Basic profile info"""

    owner = Principal(title=_("Profile owner"))

    owner_title = TextLine(title=_("Profile owner"),
                           readonly=True)

    def getAuthenticatorPlugin(self):
        """Get authentication plug-in"""

    def isExternal(self):
        """Check if profile is matching an external principal"""


class IProfileActivationInfo(Interface):
    """Profile activation info"""

    self_registered = Bool(title=_("Self-registered profile?"),
                           description=_("'No' means that profile creation was requested by another user"),
                           required=True,
                           default=True,
                           readonly=True)

    activation_secret = TextLine(title=_("Activation secret key"),
                                 description=_("This activation secret key is used to generate activation hash"))

    activation_hash = TextLine(title=_("Activation string"),
                               description=_("This activation hash string is provided in the activation message URL"))

    activation_date = Datetime(title=_("Activation date"))

    activated = Bool(title=_("Activated profile?"),
                     description=_("If 'Yes', the profile owner activated his account and changed his password"),
                     required=True,
                     default=False)

    def generateSecretKey(self, login, password):
        """Generate secret key for given profile"""

    def checkActivation(self, hash, login, password):
        """Check activation for given settings"""


class IProfileActivationAdminInfo(Interface):
    """Profile settings only defined by application administrator"""

    filtered_uploads = Bool(title=_("Filtered uploads"),
                            description=_("If 'Yes', uploaded packets are filtered for invalid contents"),
                            required=True,
                            default=True)

    disabled_upload = Bool(title=_("Disabled upload?"),
                           description=_("If 'Yes', uploading new packets is disabled"),
                           required=True,
                           default=False)

    disabled_upload_date = Datetime(title=_("Disable upload date"),
                                    required=False)

    disabled = Bool(title=_("Disabled profile?"),
                    description=_("If 'Yes', uploading and downloading of any packet is disabled and user can't use this service anymore"),
                    required=True,
                    default=False)

    disabled_date = Datetime(title=_("Disable date"),
                             required=False)


class IProfileQuotaInfo(Interface):
    """Profile quotas interface"""

    quota_size = Int(title=_("User quota size"),
                     description=_("User quota size is given in megabytes. Keep empty to get default system setting, 0 for unlimited quota"),
                     required=False)

    quota_size_str = Int(title=_("Quota size"),
                         description=_("Maximum allowed storage, in megabytes. 'None' means that you don't have any limit."),
                         readonly=True)

    quota_usage = Int(title=_("Current quota usage"),
                      readonly=True)

    max_documents = Int(title=_("User max documents count"),
                        description=_("Maximum number of documents which can be send in a single packet. Keep empty to get default system setting, 0 for unlimited number"),
                        required=False)

    max_documents_str = Int(title=_("Max documents count"),
                            description=_("Maximum number of documents which can be send in a single packet. 'None' means that you don't have any limit."),
                            readonly=True)

    def getQuotaSize(self, context):
        """Get user quota size"""

    def getQuotaUsage(self, context):
        """Get user quota usage"""

    def getMaxDocuments(self, context):
        """Get user maximum documents sount"""


class IProfile(IProfileInfo, IProfileActivationInfo, IProfileActivationAdminInfo, IProfileQuotaInfo):
    """User profile settings info
    
    Profile define principal settings and is stored in principals annotations utility"""


#
# Profiles cleaner task interfaces
#

class IProfilesCleanerTaskInfo(Interface):
    """Profiles cleaner task info"""


class IProfilesCleanerTask(IProfilesCleanerTaskInfo, ISchedulerTask):
    """Profiles cleaner task interface"""
