from setuptools import setup

the_version='0.1.4'

setup(
    name = 'weechat_notifier',
    version = the_version,
    packages = ['weechat_notifier'],
    description = 'Weechat Notification Plugin',
    author='Fenton Travers',
    author_email='fenton.travers@gmail.com',
    url='https://pypi.python.org/packages/source/w/weechat_notifier/weechat_notifier-' + the_version + '.tar.gz',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description='A notification plugin for weechat',
    classifiers=[
        'Programming Language :: Python :: 3.3',
    ]
)
