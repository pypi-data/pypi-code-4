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

from cStringIO import StringIO
import re

from lxml import etree

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams

from credicoop.resume import Resumen, ResumenDetalle
from credicoop.constants import CODEC, TITLE, TITLE_PREV, TITLE_LAST


class ParseCredicoop(object):

    def __init__ (self, filename):
        self.filename = filename
        self.content = self.get_content()

    def get_content(self):

        doc = self.convert_pdf()
        tree = etree.HTML(doc)
        content = tree.xpath("/html/body//span/text()")

        new_line = []
        for x in content:
            line = x.strip()
            if line:
                new_line.append(line)

        return new_line

    def convert_pdf(self):

        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = CODEC
        laparams = LAParams()
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

        fp = file(self.filename, 'rb')

        process_pdf(rsrcmgr, device, fp)
        fp.close()
        device.close()

        str = retstr.getvalue()
        retstr.close()
        return str


    def create(self):

        resumen = Resumen()

        for line in self.content:
            line = line

            #if all([x in TITLE for x in line.split()]):
            #    flag = True

            if TITLE_PREV in line:
                saldo_anterior = line.strip().strip(TITLE_PREV)
                resumen.saldo_anterior = self._format_money(saldo_anterior)

            elif TITLE_LAST in line:
                fecha, saldo = line.strip().strip(TITLE_LAST).split()
                resumen.saldo = self._format_money(saldo)
                resumen.fecha_saldo = fecha

            elif re.search(r'(^\d+/\d+/\d+)', line) and not resumen.fecha_saldo:
                detalle = ResumenDetalle()

                detalle.fecha = line[0:8]
                detalle.comprobante = line[9:21].strip()
                detalle.descripcion = line[21:50].strip()
                detalle.debito = self._format_money(line[50:65])
                detalle.credito = self._format_money(line[65:98])
                detalle.saldo = self._format_money(line[85:])

                resumen.items.append(detalle)

        return resumen

    def _format_money(self, data):
        data = data.strip()
        data = data.replace('.', '')
        data = data.replace(',', '.')
        data = data.encode('utf-8')

        if '−' in data or '-' in data:
            data = '-' + data.replace('−', '')

        return data

