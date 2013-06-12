#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright 2013 Alberto Paparelli (a.k.a. carpediem)
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  https://github.com/carpe-diem/resumen-credicoop/

import getopt
import sys

from credicoop.process import ParseCredicoop
from credicoop.constants import TITLE, TITLE_PREV, TITLE_LAST


def main(argv):

    def usage():
        print ('usage: %s -f <filename> [--fazio]' % argv[0])
        return 100

    try:
        (opts, args) = getopt.getopt(argv[1:], 'f:', 'fazio')
    except getopt.GetoptError:
        return usage()

    for opt, arg in opts:
        if opt == '-h':
            return usage()
        if opt == ("-f"):
            filename = arg
        if opt == ("--fazio"):
            fazio = True
        else:
            fazio = False

    try:
        credicoop = ParseCredicoop(filename)
        obj = credicoop.create()

        if fazio:
            from credicoop.export import ResumeXLS
            book = ResumeXLS(obj)

        else:
            print u"{0}{1}\n".format(
                TITLE_PREV.rjust(20), obj.saldo_anterior.rjust(30))

            print u"{0}{1}{2}{3}{4}{5}".format(
                    TITLE[0].rjust(0),
                    TITLE[1].rjust(20),
                    TITLE[2].rjust(30),
                    TITLE[3].rjust(20),
                    TITLE[4].rjust(15),
                    TITLE[5].rjust(10))

            for x in obj.items:
                "{}".rjust(4)
                print u"{0}{1}{2}{3}{4}{5}".format(
                    x.fecha.rjust(10),
                    x.comprobante.rjust(10),
                    x.descripcion.rjust(40),
                    x.debito.rjust(15),
                    x.credito.rjust(15),
                    x.saldo.rjust(15))

            print u"\n{0}{1}{2}".format(TITLE_LAST.rjust(20), obj.fecha_saldo.rjust(10),
                    obj.saldo.rjust(20))


    except Exception, e:
        print e


if __name__ == "__main__":
    sys.exit(main(sys.argv))


