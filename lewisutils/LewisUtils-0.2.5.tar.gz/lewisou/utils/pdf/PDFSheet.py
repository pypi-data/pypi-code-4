#!/usr/bin/env python

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import sys

class PDFSheet:
    def __init__ (self, pagesize=letter, rows=4, cols=3, font='Helvetica', font_size=20, left_adj=0.2*inch):
        self.pagesize = pagesize
        self.rows = rows
        self.cols = cols
        self.font = font
        self.font_size = font_size
        self.p_width, self.p_height = self.pagesize
        self.block_width, self.block_height, = (self.p_width - 2 * left_adj) / self.cols, self.p_height / self.rows
        self.left_adj = left_adj

    def set_data (self, data_list):
        """
        data_list = [
        [(x, y, max_num_of_characters_per_line, 'text'),
        (x, y, max_num_of_characters_per_line, 'text'),
        (x, y, max_num_of_characters_per_line, 'text')],
 
        [(x, y, max_num_of_characters_per_line, 'text'),
        (x, y, max_num_of_characters_per_line, 'text'),
        (x, y, max_num_of_characters_per_line, 'text')],
        ]
        """
        self.data_list = data_list

    def render (self):
        c = canvas.Canvas (sys.stdout, self.pagesize)
        c.setFont (self.font, self.font_size)

        for idx, block in enumerate(self.data_list):
            cur_col = (idx / self.rows) % self.cols
            cur_row = idx % self.rows
            # if cur_col == 0:
            #     ladj = self.left_adj
            # else:
            #     ladj = 0

            origin = (self.left_adj + cur_col * self.block_width,
                      (self.rows - cur_row - 1) * self.block_height)

            textobject = c.beginText()
            for entry in block:
                # c.drawString(origin[0] + entry[0] * inch,
                #              origin[1] + entry[1] * inch,
                #              entry[3])
                textobject.setTextOrigin(origin[0] + entry[0] * inch,
                                         origin[1] + entry[1] * inch)
                # textobject.setFont(self.font, self.font_size)
                for l in split_with_num (entry[3], entry[2]):  
                    textobject.textLine(l)

            c.drawText(textobject)
            # seperate pages
            if (idx + 1) % (self.rows * self.cols) == 0:
                # print 'new Page'
                c.showPage()
                c.setFont (self.font, self.font_size)
        c.save()

def split_with_num (s, n):
    """
    >>> [i for i in split_with_num ('123', 1)]
    ['1', '2', '3']
    """
    while len (s) > n:
        yield s[:n]
        s = s[n:]
    yield s

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 't':
        import doctest
        doctest.testmod()
    else:
        p = PDFSheet (font_size=20)
        p.set_data ([
            [(1, 2, 1, "1234")],
            [(1, 2, 2, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
            [(1, 2, 100, "1000")],
        ])
        p.render ()
