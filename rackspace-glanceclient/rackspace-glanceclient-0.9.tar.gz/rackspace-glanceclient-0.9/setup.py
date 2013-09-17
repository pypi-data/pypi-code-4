#   Copyright 2013 Rackspace
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import setuptools


setuptools.setup(
    name='rackspace-glanceclient',
    version='0.9',
    author='Rackspace',
    author_email='brian.rosmaita@rackspace.com',
    description='Metapackage to install python-glanceclient and Rackspace '
                'auth package',
    license='Apache License, Version 2.0',
    url='https://github.com/ostackbrian/rackspace-glanceclient',
    install_requires=['python-glanceclient', 'rackspace-auth-openstack'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        #"Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ]
)
