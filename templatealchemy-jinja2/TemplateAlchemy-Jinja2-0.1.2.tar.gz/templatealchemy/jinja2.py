# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  templatealchemy.jinja2
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/07/03
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

from __future__ import absolute_import

import jinja2
from templatealchemy import api, util

#------------------------------------------------------------------------------
def loadRenderer(spec=None):
  return Jinja2Renderer(spec)

#------------------------------------------------------------------------------
class Jinja2Renderer(api.Renderer):

  #----------------------------------------------------------------------------
  def __init__(self, spec):
    # TODO: expose control of `jinja2.template.Template()` args/kwargs...
    self.spec = spec

  #----------------------------------------------------------------------------
  def render(self, context, data, params):
    tpl = jinja2.Template(data)
    return tpl.render(**params)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
