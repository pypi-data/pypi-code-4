# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/09/09
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

from .controller import DescribeController

def includeme(config):
  '''
  Includes pyramid-inspect functionality into the pyramid application
  specified by `config`. See the main documentation for accepted
  configurations.
  '''
  controller = DescribeController()
  # config.add_view(...)
  # raise NotImplementedError()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
