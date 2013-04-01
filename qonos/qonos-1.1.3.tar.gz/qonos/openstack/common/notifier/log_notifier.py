# Copyright 2011 OpenStack Foundation.
# All Rights Reserved.
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

from oslo.config import cfg

from qonos.openstack.common import jsonutils
from qonos.openstack.common import log as logging


CONF = cfg.CONF


def notify(_context, message):
    """Notifies the recipient of the desired event given the model.
    Log notifications using openstack's default logging system"""

    priority = message.get('priority',
                           CONF.default_notification_level)
    priority = priority.lower()
    logger = logging.getLogger(
        'qonos.openstack.common.notification.%s' %
        message['event_type'])
    getattr(logger, priority)(jsonutils.dumps(message))
