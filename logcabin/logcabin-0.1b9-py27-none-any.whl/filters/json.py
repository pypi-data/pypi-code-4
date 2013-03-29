# avoid naming ambiguity over stdlib json
from __future__ import absolute_import

from .filter import Filter
import json

class Json(Filter):
    """Parse a json encoded field.

    :param string field: the field containing the json (default: data)
    :param boolean consume: whether to remove the field after decoding (default: true)
    """

    def __init__(self, field='data', consume=True, on_error='reject'):
        super(Json, self).__init__(on_error=on_error)
        self.field = field
        self.consume = consume

    def process(self, event):
        if self.field in event:
            if self.consume:
                data = event.pop(self.field)
            else:
                data = event[self.field]

            try:
                j = json.loads(data)
                self.logger.debug('JSON decoded: %s' % j)
                event.update(j)
                return True
            except ValueError as ex:
                self._error(event, ex)
                return False
