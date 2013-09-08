from setuptools import setup
version='0.1.40'
name='weechat_notifier'
classifiers = [
        'Programming Language :: Python :: 3.3',
    ]
setup(
    name = name,
    version = version,
    packages = [name],
    description = 'Weechat Notification Plugin',
    author='Fenton Travers',
    author_email='fenton.travers@gmail.com',
    url='https://pypi.python.org/packages/source/w/weechat_notifier/weechat_notifier-' + version + '.tar.gz',
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description='A notification plugin for weechat',
    classifiers=classifiers
)
