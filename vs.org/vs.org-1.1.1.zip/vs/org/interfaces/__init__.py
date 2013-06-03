################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: __init__.py 2981 2011-03-16 10:54:12Z carsten $

from zope.interface import Interface

# -*- extra stuff goes here -*-
from base import IBase
from employee import IEmployee
from employeefolder import IEmployeefolder
from department import IDepartment
from institution import IInstitution
from vcard import IVCardData
from addresses import IAddressProvider
from keywords import IKeywordExtractor

