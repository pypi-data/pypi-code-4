import sys

import setuptools

py26_reqs = ['argparse', 'importlib'] if sys.version_info < (2,7) else []

setuptools.setup(
    name='librarypaste',
    use_hg_version=dict(increment='0.1'),
    author='Jamie Turner',
    author_email='jamie@jamwt.com',
    url='http://bitbucket.org/chmullig/librarypaste/',
    description='Simple pastebin',
    long_description='Simple pastebin',
    license='MIT',
    packages=['librarypaste'],
    package_dir={'librarypaste': 'librarypaste'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'librarypaste=librarypaste.librarypaste:main',
        ],
    },
    install_requires=[
        'pygments',
        'Mako',
        'cherrypy',
        'PyYAML',
    ] + py26_reqs,
    setup_requires=[
        'hgtools',
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
    zip_safe=False,
)
