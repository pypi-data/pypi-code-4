#
# Copyright 2013 Wantoto Inc http://www.wantoto.com/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import sys


cwd = os.getcwd()

# Read fss_settings
fss_settings = {
    'cwd': cwd,
    'static_folder': 'static',
    'templates_folder': 'templates',
    'templates_context': {},
    'output_folder': '.',
}
if os.path.exists(os.path.join(cwd, 'fss_settings.py')):
    # add current cwd into python path
    sys.path.append(cwd)
    local_settings = {key: value for key, value in __import__('fss_settings').__dict__.items()
                      if not key.startswith('__') and not key.endswith('__')}
    sys.path.pop()
    # Update
    fss_settings.update(local_settings)
