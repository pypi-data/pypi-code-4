#!/usr/bin/env python
#
# Copyright (C) 2009-2012 W. Trevor King <wking@tremily.us>
#
# This file is part of unfold_protein.
#
# unfold_protein is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# unfold_protein is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# unfold_protein.  If not, see <http://www.gnu.org/licenses/>.

"""Run a mechanical protein unfolding experiment."""

import os
import os.path

import numpy as _numpy

from unfold_protein import __version__
import unfold_protein.storage as _storage


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description=__doc__, version=__version__)
    parser.add_argument(
        '-s', '--song',
        help='Path to a song to play when the experiment is complete')
    parser.add_argument(
        '-S', '--no-stepper-tweaks', dest='stepper_tweaks',
        action='store_const', const=False, default=True,
        help=("Don't move the stepper except for the initial approach "
              "and final retraction"))

    args = parser.parse_args()

    devices = []
    try:
        scanner = _storage.load_scanner()
        scanner.load_from_config(devices=devices)
        scanner.unfolder.afm.piezo.zero()
        scanner.run(stepper_tweaks=args.stepper_tweaks)
    finally:
        scanner.unfolder.afm.move_away_from_surface()
        scanner.unfolder.afm.piezo.zero()
        for device in devices:
            device.close()
        if args.song:
            song = os.path.abspath(os.path.expanduser(args.song))
            os.system("aplay '%s'" % song)
