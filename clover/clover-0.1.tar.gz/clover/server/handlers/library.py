import os

from clover.server.handlers.base import Base
from clover import get_package_resource

__dir__ = os.path.dirname(os.path.abspath(__file__))

javascript_library_root = get_package_resource('javascript')


class Handler(Base):
    def get(self, path):
        self.response.headers['Content-Type'] = 'application/javascript'
        self.response.write(open(os.path.join(javascript_library_root, path)).read())

        