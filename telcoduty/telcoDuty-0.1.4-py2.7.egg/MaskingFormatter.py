__author__ = 'alexey.grachev'

class MaskingFormatter(object):
    """
    """
    def __init__(self, formatter, masks, replacer='*'):
        self._formatter = formatter
        self._masks = masks
        self._replacer = replacer
        self._repeateReplacer = 8


    def formatTime(self, record, datefmt=None):
        """
        """
        return self._formatter.formatTime(record, datefmt)

    def formatException(self, exc_info):
        """
        """
        return self._formatter.formatException(exc_info)

    def format(self, record):
        """
        """
        message = self._formatter.format(record)
        for mask in self._masks:
            message = message.replace(mask, '*' * self._repeateReplacer)
        return message