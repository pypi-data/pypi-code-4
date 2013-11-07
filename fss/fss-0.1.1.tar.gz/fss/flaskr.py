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
import json
from flask import Flask, render_template
import os


# Read settings
SETTINGS = {
    'static_folder': 'static',
    'templates_folder': 'templates',
    'output_folder': '.',
}
SETTINGS_PATH = os.path.join(os.getcwd(), 'fss.json')
if os.path.exists(SETTINGS_PATH):
    with open(SETTINGS_PATH, 'r') as f:
        try:
            SETTINGS.update(json.load(f))
        except ValueError:
            print('\x1B[33mFailed to parse fss.json. Use default settings\x1B[m')

# Create app
app = Flask(
    __name__,
    static_folder=os.path.join(os.getcwd(), SETTINGS['static_folder']),
    template_folder=os.path.join(os.getcwd(), SETTINGS['templates_folder'])
)

# Configure app and freezer
app.debug = True
app.config['FREEZER_REMOVE_EXTRA_FILES'] = False
app.config['FREEZER_DESTINATION'] = os.path.join(os.getcwd(), SETTINGS['output_folder'])
if 'flask_app_config' in SETTINGS:
    app.config.update(SETTINGS['flask_app_config'])


# Load page
@app.route('/', defaults={'path_name': 'index.html'})
@app.route('/<path:path_name>')
def load_page(path_name):
    path_without_ext, ext = os.path.splitext(path_name)
    return render_template(os.path.join(path_without_ext, 'index.jinja') if not ext else path_without_ext + '.jinja')


# Main section
if __name__ == '__main__':
    app.run()
