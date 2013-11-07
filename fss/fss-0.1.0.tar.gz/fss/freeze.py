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
from flask_frozen import Freezer, os
from flaskr import app

freezer = Freezer(app)


@freezer.register_generator
def load_page():
    # Collect jinja paths
    #noinspection PyUnusedLocal
    def visit(x, folder, files):
        for file_name in files:
            path = os.path.join(folder, file_name)
            if path.endswith('.jinja') and not file_name.startswith('_') and not os.path.isdir(path):
                jinja_paths.append(os.path.relpath(path, app.template_folder))
    jinja_paths = []
    os.path.walk(app.template_folder, visit, 0)

    # Convert to html paths
    html_paths = map(lambda path: path.replace('.jinja', '.html'), jinja_paths)

    # Go
    for html_path in html_paths:
        print('Build \x1B[1;36m{0}\x1B[m'.format(html_path))
        yield {'path_name': html_path}

    print('\x1B[1;32mDone\x1B[m')


if __name__ == '__main__':
    freezer.freeze()
