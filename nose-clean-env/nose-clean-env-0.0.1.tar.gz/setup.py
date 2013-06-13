
from distutils.core import setup

setup(
    name='nose-clean-env',
    py_modules=['nose_clean_env'],
    version="0.0.1",
    description="Nose Clean Env restores os.environ after each test",
    author="Eric Olson",
    author_email="mail@olsoneric.com",
    maintainer="Eric Olson",
    maintainer_email="mail@olsoneric.com",
    url="http://github.com/olsoneric/nose-clean-env",
    keywords=["nose", "plugins", "os.environ", "os", "env", "environment"],
    entry_points={
        'nose.plugins.0.10': [
            'nose_clean_env = nose_clean_env:NoseCleanEnv'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    long_description="""\
Nose Clean Env
-------------------------------------
The Nose Clean Env nose plugin restores Python's os.environ after
    each test.

The purpose of the plugin is to prevent a test's modifications to
os.environ from affecting other tests.

"""
)
