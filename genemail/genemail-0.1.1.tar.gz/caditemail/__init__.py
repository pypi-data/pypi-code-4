# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  caditapp.email
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2012/11/20
# copy: (C) Copyright 2012 Cadit Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import sys
from .manager import *
from .sender import *
from .emailprov import *

#------------------------------------------------------------------------------
if __name__ == '__main__':
  from cli import main
  sys.exit(main())

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
