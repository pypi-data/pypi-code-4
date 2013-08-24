# -*- coding: utf-8 -*-
#
# src/configviper/lockfile/posixlocker.py
# https://bitbucket.org/danielgoncalves/configviper
#
# ConfigViper  Copyright (C) 2013  Daniel Gonçalves <daniel@base4.com.br>
#
# This file is part of ConfigViper.
#
# ConfigViper is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
#
# ConfigViper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ConfigViper. If not, see <http://www.gnu.org/licenses/>.
#

import fcntl

from . import PortaLocker

class PosixPortaLocker(PortaLocker):
    """File lock implementation based on ``fcntl.lockf`` function for
    exclusive file locking (``fcntl.LOCK_EX``).
    """

    def __init__(self, filename, mode, encoding='utf-8', ignore_encoding=False):
        super(PosixPortaLocker, self).__init__(
                filename, mode,
                encoding=encoding,
                ignore_encoding=ignore_encoding)


    def _lock_impl(self):
        # there is no return value; if lock fails an exception will be raised
        fcntl.lockf(self.file_object.fileno(), fcntl.LOCK_EX)
        return True


    def _unlock_impl(self):
        # there is no return value; if unlock fails an exception will be raised
        fcntl.lockf(self.file_object.fileno(), fcntl.LOCK_UN)
        return True
