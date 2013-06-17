import os


def term_size():
    # http://stackoverflow.com/questions/566746/
    #   how-to-get-console-window-width-in-python
    rows, cols = os.popen('stty size', 'r').read().strip().split()
    return int(rows), int(cols)
