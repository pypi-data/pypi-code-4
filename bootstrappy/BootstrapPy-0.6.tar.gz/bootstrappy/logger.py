import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = dict(DEBUG=BLUE,
              INFO=WHITE,
              WARNING=YELLOW,
              ERROR=RED,
              CRITICAL=MAGENTA)

COLOR_SEQ = '\033[1;{0}m{1}\033[0m'


class ColorFormatter(logging.Formatter):
    """Custom log formatter which colorizes console output

    """

    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        level = record.levelname
        msg = record.msg
        color = str(30 + COLORS[level])
        if level in COLORS:
            record.levelname = COLOR_SEQ.format(color, level)
            record.msg = COLOR_SEQ.format(color, msg)
        return logging.Formatter.format(self, record)