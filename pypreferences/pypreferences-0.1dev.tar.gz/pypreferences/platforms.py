import platform
from custom_types import enum
from managers.mac_manager import MacManager

PlatformEnum = enum(
    'Windows',
    'Macintosh',
    'Linux',
)

platforms = {}


class PlatformMeta(type):

    def __init__(cls, *args):
        super(PlatformMeta, cls).__init__(args)

        if cls.platform is None:
            return

        platforms[cls.platform] = cls


class Platform(object):
    __metaclass__ = PlatformMeta
    platform = None

    @staticmethod
    def is_current_platform():
        return False

    @staticmethod
    def get_manager():
        return None


class Windows(Platform):
    platform = PlatformEnum.Windows

    @staticmethod
    def is_current_platform():
        return "Windows" in platform.system()


class Macintosh(Platform):
    platform = PlatformEnum.Macintosh

    @staticmethod
    def is_current_platform():
        return "Darwin" in platform.system()

    @staticmethod
    def get_manager():
        return MacManager
    

class Linux(Platform):
    platform = PlatformEnum.Linux

    @staticmethod
    def is_current_platform():
        return "Linux" in platform.system()
