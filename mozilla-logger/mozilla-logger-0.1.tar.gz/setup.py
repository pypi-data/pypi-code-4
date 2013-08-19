from setuptools import setup


setup(
    name='mozilla-logger',
    version='0.1',
    description='Django interface with statsd',
    long_description=open('README.rst').read(),
    author='Andy McKay',
    author_email='andym@mozilla.com',
    license='MPL',
    packages=['mozilla_logger'],
    url='https://github.com/andymckay/mozilla-logger',
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Framework :: Django'
    ]
)
