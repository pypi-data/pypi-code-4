################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id$

from Products.validation import validation
from validators import isVsAddress
validation.register(isVsAddress)

