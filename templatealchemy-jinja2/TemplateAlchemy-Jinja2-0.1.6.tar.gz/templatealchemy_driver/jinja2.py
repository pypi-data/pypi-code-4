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

  # TODO: expose control of `jinja2.template.Template()` args/kwargs...

  #----------------------------------------------------------------------------
  def render(self, context, stream, params):
    tpl = jinja2.Template(stream.read())
    return tpl.render(**params)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
