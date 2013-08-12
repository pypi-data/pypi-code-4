from random import randrange, choice, shuffle
from netaddr import *
from sample_data_utils.numeric import hexnum

NOT_NET = [10, 127, 172, 192, 169]
PRIVATE_NET = ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16']
DEDICATED_NET = ['100.64.0.0/10', ]
LOCAL_NET = ['169.254.0.0/16', '127.0.0.0/8']

NO_PUBLIC = PRIVATE_NET + DEDICATED_NET + LOCAL_NET + ['192.0.2.0/24', '192.88.99.0/24', '198.18.0.0/15']


def ipaddress(not_valid=None):
    """
        returns a string representing a random ip address

    :param not_valid: if passed must be a list of integers representing valid class A netoworks that must be ignored
    """
    not_valid_class_A = not_valid or []

    class_a = [r for r in range(1, 256) if r not in not_valid_class_A]
    shuffle(class_a)
    first = class_a.pop()

    return ".".join([str(first), str(randrange(1, 256)),
                     str(randrange(1, 256)), str(randrange(1, 256))])


def ip(private=True, public=True, max_attempts=10000):
    """
        returns a :class:`netaddr.IPAddress` instance with a random value

    :param private: if False does not return private networks
    :param public:  if False does not return public networks
    :param max_attempts:
    """
    if not (private or public):
        raise ValueError('Cannot disable both `private` and `public` network')

    if private != public:
        if private:
            is_valid = lambda address: address.is_private()
            not_valid = [n for n in range(1, 255) if n not in NOT_NET]
        else:
            is_valid = lambda address: not address.is_private()
            not_valid = NOT_NET

        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            ip = IPAddress(ipaddress(not_valid))
            if is_valid(ip):
                return ip
    else:
        return IPAddress(ipaddress())


def ipv4():
    return IPAddress(ipaddress()).ipv4()


def ipv6():
    return IPAddress(ipaddress()).ipv6()


def node(network):
    return str(choice(list(IPNetwork(network))))


def mac_address(vendors=True):
    manufactures = ('00:24:e8:',  # Dell Inc.
                    '00:21:6a:',  # intel
                    '08:00:27:',  # cadmus computer systems
                    )
    if vendors:
        return choice(manufactures) + ":".join([hexnum(2) for i in range(3)])
    else:
        return ":".join([hexnum(2) for i in range(6)])
