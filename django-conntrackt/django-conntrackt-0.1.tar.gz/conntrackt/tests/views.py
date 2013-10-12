# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Branko Majic
#
# This file is part of Django Conntrackt.
#
# Django Conntrackt is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django Conntrackt is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
#


# Application imports.
from conntrackt.views import RedirectToNextMixin


class StaticSuccessUrlFakeMixin(object):
    """
    Helper view for testing the RedirectToNextMixinView mixin.
    """

    def get_success_url(self):
        return self.success_url


class RedirectToNextMixinView(RedirectToNextMixin, StaticSuccessUrlFakeMixin):
    """
    Helper view for testing the RedirectToNextMixinView mixin. StaticSuccessUrl
    is there just to provide default for get_success_url().
    """

    success_url = "/STATIC"

    def __init__(self, request):
        """
        Initialise the request to provided value.
        """

        self.request = request
