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

from decimal import Decimal

try:
    from xlwt import Workbook
    from xlwt import Font
    from xlwt import XFStyle
    from xlwt import Borders
    from xlwt import Formula
except ImportError, e:
    raise ImportError("Falta instalar xlwt")

from credicoop.utils import slugify


class ResumeXLS(object):

    def __init__(self, data):
        self.data = data
        self.book = Workbook()

        self.page_banco()

        self.save()

    def save(self):
        filename = slugify(self.data.__repr__()) + '.xls'
        self.book.save(filename)
        print "\n\nSe creo el archivo {}\n\n".format(filename)

    def page_banco(self):
        ws1 = self.book.add_sheet('BANCO')

        header_font = Font()
        content_font = Font()

        # Header font preferences
        header_font.name = 'Arial'
        header_font.height = 20 * 10
        header_font.bold = True

        # Body font preferences
        content_font.name = 'Arial'

        # Header Cells style definition
        header_style = XFStyle()
        header_style.font = header_font

        borders = Borders()
        borders.left = 2
        borders.right = 2
        borders.top = 2
        borders.bottom = 2
        header_style.borders = borders

        content_style = XFStyle()
        content_style.font = content_font

        borders_content = Borders()
        borders_content.left = 1
        borders_content.right = 1
        content_style.borders = borders_content

        ws1.col(0).width = 3000
        ws1.col(1).width = 10000
        ws1.col(2).width = 4000
        ws1.col(3).width = 10000
        ws1.col(4).width = 4000

        ws1.write(0, 0, 'CAJA', header_style )
        ws1.write(0, 3, 'SALDO DE INICIO', header_style )
        ws1.write_merge(1, 1, 1, 2, 'INGRESO', header_style)
        ws1.write_merge(1, 1, 3, 4, 'EGRESO', header_style)
        ws1.write(2, 0, 'FECHA', header_style )
        ws1.write(2, 1, 'DETALLE', header_style )
        ws1.write(2, 2, 'MONTO', header_style )
        ws1.write(2, 3, 'DETALLE', header_style )
        ws1.write(2, 4, 'MONTO', header_style )

        data = self.data

        ws1.write(0, 4, Decimal(data.saldo_anterior), header_style )

        START_CONTENT_ROW = 3
        for i in range(0, len(data.items)):
            item = data.items[i]
            ws1.write(START_CONTENT_ROW+i, 0, item.fecha, content_style)

            if item.credito:
                ws1.write(START_CONTENT_ROW+i, 1, item.descripcion, content_style)
                ws1.write(START_CONTENT_ROW+i, 2, Decimal(item.credito), content_style)
            if item.debito:
                ws1.write(START_CONTENT_ROW+i, 3, item.descripcion, content_style)
                ws1.write(START_CONTENT_ROW+i, 4, Decimal(item.debito), content_style)

        SUM_ROW = START_CONTENT_ROW + i + 1
        SUM_BEGIN = START_CONTENT_ROW + 1
        SUM_END = START_CONTENT_ROW + i + 1

        ws1.write(SUM_ROW, 2, Formula("SUM(C{begin}:C{end})".format(
            begin=SUM_BEGIN, end=SUM_END)), header_style)
        ws1.write(SUM_ROW, 4, Formula("SUM(E{begin}:E{end})".format(
            begin=SUM_BEGIN, end=SUM_END)), header_style)


        LAST_ROW = START_CONTENT_ROW + i + 3

        ws1.write(LAST_ROW,3 , "SALDO AL FINAL DEL MES", header_style)
        ws1.write(LAST_ROW, 4, Decimal(data.saldo), header_style)
