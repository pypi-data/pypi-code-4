from decimal import Decimal
import json


class _number_str(float):
    # kludge to have decimals correctly output as JSON numbers;
    # converting them to strings would cause extra quotes

    def __init__(self, o):
        self.o = o

    def __repr__(self):
        return str(self.o)


class JSONEncoder(json.JSONEncoder):
    """Custom encoder that supports Decimal.
    """
    def default(self, o):

        if isinstance(o, Decimal):
            return _number_str(o)

        return super(JSONEncoder, self).default(o)  # pragma: no cover
