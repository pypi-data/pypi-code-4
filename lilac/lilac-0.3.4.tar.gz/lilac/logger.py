# coding=utf8

"""logger for lilac"""

from utils import colored

import logging
from logging import Formatter
from logging import getLogger
from logging import StreamHandler
from datetime import datetime


class ColoredFormatter(Formatter):
    """colored output formatter"""

    def format(self, record):
        message = record.getMessage()

        mapping = {
            'CRITICAL': 'bgred',
            'ERROR': 'red',
            'WARNING': 'yellow',
            'SUCCESS': 'green',
            'INFO': 'cyan',
            'DEBUG': 'bggrey',
        }
        color = mapping.get(record.levelname, 'white')

        level = colored('%-8s' % record.levelname, color)
        time = colored(datetime.now().strftime("(%H:%M:%S)"), "magenta")
        return " ".join([level, time, message])


logger = getLogger('lilac')
# add colored handler
handler = StreamHandler()
formatter = ColoredFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# add level 'success'
logging.SUCCESS = 25  # 25 is between WARNING(30) and INFO(20)
logging.addLevelName(logging.SUCCESS, 'SUCCESS')
logger.success = lambda msg, *args: logger._log(logging.SUCCESS, msg, args)


if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    logger.info('info')
    logger.success('success')
    logger.debug('debug')
    logger.warning('warning')
    logger.error('error')
    logger.critical('critical')
