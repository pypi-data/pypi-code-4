#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
Batch Parameter Views
"""

from ... import View


__all__ = ['BatchParamsView']


class BatchParamsView(View):

    provider_name = None

    def render_kwargs(self):
        return {}

    def __call__(self):
        if self.request.POST:
            if self.set_batch_params():
                return HTTPFound(location=self.request.get_referer())
        kwargs = self.render_kwargs()
        kwargs['provider'] = self.provider_name
        return kwargs


def includeme(config):
    config.include('tailbone.views.batches.params.labels')
