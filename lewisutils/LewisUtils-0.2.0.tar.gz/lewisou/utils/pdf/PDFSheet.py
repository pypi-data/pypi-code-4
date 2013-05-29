from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import sys

class PDFSheet:
    def __init__ (self, pagesize=letter, rows=4, cols=3, font='Helvetica', font_size=20):
        self.pagesize = pagesize
        self.rows = rows
        self.cols = cols
        self.font = font
        self.font_size = font_size
        self.p_width, self.p_height = self.pagesize
        self.block_width, self.block_height, = self.p_width / self.cols, self.p_height / self.rows

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
        # c = canvas.Canvas("a.pdf", self.pagesize)
        # print (self.block_width, self.block_height)

        for idx, block in enumerate(self.data_list):
            cur_row = (idx / self.cols) % self.rows
            cur_col = idx % self.cols
            # print "row: {}, col: {}".format (cur_row, cur_col)
            
            origin = (cur_col * self.block_width,
                      (self.rows - cur_row - 1) * self.block_height)
            # print "origin: {}".format(origin)

            for entry in block:
                # c.drawString(100,100,"Hello World")
                c.drawString(origin[0] + entry[0],
                             origin[1] + entry[1],
                             entry[3])

            # seperate pages
            if (idx + 1) % (self.rows * self.cols) == 0:
                # print 'new Page'
                c.showPage()
                c.setFont (self.font, self.font_size)
        c.save()

if __name__ == '__main__':
    p = PDFSheet (font_size=20)
    p.set_data ([
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
        [(1, 2, 100, "1000")],
        [(1, 2, 100, "1000")],
    ])

    p.render ()
