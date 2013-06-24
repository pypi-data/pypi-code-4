
import uuid
import datetime

def get_uuid(length=32):
    """ Return an uuid of a given length"""
    return uuid.uuid4().hex[:length]

def get_integer(value='0'):
    """ Text to int or zero """
    try:
        return int(value)
    except:
        return 0

def get_days_ago(days=0):
    """ Return X 'days' ago in datetime format """

    return (datetime.date.today() - datetime.timedelta(days))

def get_days_from_now(days=0):
    """ Return X 'days' from today in datetime format """

    return (datetime.date.today() + datetime.timedelta(days))

def get_to_binary(decimal_number, length=32):
    """ Given a decimal number, returns a string bitfield of length = len """

    bitstr = "".join(map(lambda y: str((decimal_number>>y)&1), range(length-1, -1, -1)))
    return bitstr





