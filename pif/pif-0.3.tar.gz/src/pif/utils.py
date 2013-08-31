__title__ = 'pif.utils'
__version__ = '0.3'
__build__ = 0x000003
__author__ = 'Artur Barseghyan'
__all__ = ('ensure_autodiscover', 'list_checkers', 'get_public_ip')

from pif.base import registry
from pif.discover import autodiscover

def ensure_autodiscover():
    """
    Ensures the IP checkers are discovered.
    """
    if not registry._registry:
        autodiscover()

def list_checkers():
    return registry._registry.keys()

def get_public_ip(preferred_checker=None, print_info=False):
    """
    Gets IP using one of the services.

    :param str preffered checker:
    :return str:
    """
    ensure_autodiscover()

    # If use preferred checker.
    if preferred_checker:
        ip_checker_cls = registry.get(preferred_checker)

        if not ip_checker_cls:
            return False

        ip_checker = ip_checker_cls()
        ip = ip_checker.get_public_ip()

        if print_info:
            print 'provider: ', ip_checker_cls
        return ip

    # Using all checkers.

    for ip_checker_name, ip_checker_cls in registry._registry.items():
        ip_checker = ip_checker_cls()
        try:
            ip = ip_checker.get_public_ip()
            if ip:
                if print_info:
                    print 'provider: ', ip_checker_cls
                return ip

        except Exception, e:
            pass

    return False
