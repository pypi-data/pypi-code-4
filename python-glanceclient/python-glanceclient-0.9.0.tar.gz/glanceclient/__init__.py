# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright 2012 OpenStack LLC
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

#NOTE(bcwaldon): this try/except block is needed to run setup.py due to
# its need to import local code before installing required dependencies
try:
    import glanceclient.client
    Client = glanceclient.client.Client
except ImportError:
    import warnings
    warnings.warn("Could not import glanceclient.client", ImportWarning)

from glanceclient.openstack.common import version as common_version

__version__ = common_version.VersionInfo('python-glanceclient')
