#
# Copyright 2013 the original author or authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from acme.framework.factory import Factory

class MockFactory(Factory):
    """ This factory should never be picked up
    """

    def __init__(self, widget):
        super(MockFactory, self).__init__(widget)
        raise NotImplementedError

    def work(self):
        raise NotImplementedError


def do(i):
    """ This plugin method should never be picked up
    """
    raise NotImplementedError
