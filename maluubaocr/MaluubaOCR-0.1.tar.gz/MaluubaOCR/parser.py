import arff
import sys

class Digit(object):

    def __init__(self, row):
        row_vector = [row[i] for i in range(256)]
        self.bitmap = [[row[j * 16 + i] for i in range(16)] for j in range(16)]
        self.classification = row[256]

    def draw(self, image_file):
        try:
            import cairo
        except:
            print "You don't have PyCairo installed, so you can't draw digits"
            print "Please grab it at http://cairographics.org/pycairo/"
            return

        width, height = 256, 256
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        ctx = cairo.Context(surface)

        # Fill with white
        ctx.new_path()
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()

        for i in range(16):
            for j in range(16):
                square = self.bitmap[j][i]
                # Shift the (-1, 1) interval into the (0,1) interval, with the
                # direction reversed
                color = (-square + 1) / 2.0
                ctx.set_source_rgb(color, color, color)
                ctx.new_path
                ctx.rectangle(i * 16, j * 16, 16, 16)
                ctx.fill()

        ctx.set_source_rgb(0.0, 0.0, 1.0)
        ctx.set_line_width(0.5)
        for i in range(1,16):
            ctx.move_to(0, i * 16)
            ctx.line_to(width, i * 16)
            ctx.stroke()

            ctx.move_to(i * 16, 0)
            ctx.line_to(i * 16, height)
            ctx.stroke()

        surface.write_to_png(image_file)

def load_digits(file_name):
    return [Digit(row) for row in arff.load(file_name)]

if __name__ == '__main__':
    print sys.argv[1]
    map(lambda (i, digit): digit.draw('%d_%s.png' % (i, digit.classification)), [(i, digit) for i, digit in enumerate(load_digits(sys.argv[1]))])