from fabric.api import *


def upload():
    local('python setup.py sdist upload')
