#!/usr/bin/env python
# 
# Copyright (c) 2011 Outpost Embedded, LLC
# 
# This file is part of the pylibsensors software package.
# 
# pylibsensors is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# A copy of the license has been included in the COPYING file.


import sys
from argparse import ArgumentParser

import libsensors


def main(argv):
    libsensors.init()
    try:
        parser = ArgumentParser()
        parser.add_argument('--debug', action = 'store_true', default = False)
        parser.add_argument('chip_name', nargs = '?', default = None)

        args = parser.parse_args(argv[1:])

        if args.chip_name is None:
            match = None
        else:
            match = libsensors.parse_chip_name(args.chip_name)

        for chip_name in libsensors.get_detected_chips(match):
            s = str(chip_name)
            if args.debug:
                s = '%s (%r)' % (s, chip_name)
            print s

            s = 'Adapter: %s' % libsensors.get_adapter_name(chip_name.bus)
            if args.debug:
                s = '%s (%r)' % (s, chip_name.bus)
            print s

            for feature in libsensors.get_features(chip_name):
                label = libsensors.get_label(chip_name, feature)
                value = libsensors.get_value(chip_name, feature.number)

                s = '%s: %s' % (label, value)
                if args.debug:
                    s = '%s (%r)' % (s, feature)
                print s

                for subfeature in libsensors.get_all_subfeatures(
                      chip_name,
                      feature,
                    ):
                    value = libsensors.get_value(chip_name, subfeature.number)

                    s = '  %s: %s' % (subfeature.name, value)
                    if args.debug:
                        s = '%s (%r)' % (s, subfeature)
                    print s

            print ''

    finally:
        libsensors.cleanup()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
