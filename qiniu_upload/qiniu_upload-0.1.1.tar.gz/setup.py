from qiniuupload import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'qiniu_upload',
    version = __version__,
    description = 'A simple tool makes us easier upload files to Qiniu Resource (Cloud) Storage',
    author = 'Tom.Huang',
    author_email = 'hzlhu.dargon@gmail.com',
    maintainer_email = 'hzlhu.dargon@gmail.com',
    license = 'MIT',
    url = 'https://github.com/NanJingBoy/qiniu_upload',
    packages = ['qiniuupload'],
    platforms = 'Linux',
    install_requires = [
        'qiniu',
        'termcolor'
    ],
    entry_points = {"console_scripts": ['qiniu_upload=qiniuupload.cli:run']},
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)