import os.path
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as file:
    README = file.read()

requires = [
    'pymongo',
    'flask'
]

setup(
    name='up',
    version='0.1.0',
    description='Up - A next generation status monitor',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3.3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business"
    ],
    author='Aaron Spaulding',
    author_email='aaron@sachimp.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,
    install_requires=requires,
    tests_require=requires,
    test_suite="up",
    entry_points="""\
    [console_scripts]
    up = up.status:main
    """,
)
