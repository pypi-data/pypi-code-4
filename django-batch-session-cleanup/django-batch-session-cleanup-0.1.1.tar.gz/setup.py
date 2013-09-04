from distutils.core import setup

setup(
    name='django-batch-session-cleanup',
    version='0.1.1',
    author='Kevan Carstensen',
    author_email='kevan@isnotajoke.com',
    packages=['batch_session_cleanup', 'batch_session_cleanup.management', 'batch_session_cleanup.management.commands'],
    url='https://github.com/isnotajoke/django-batch-session-cleanup',
    license='MIT',
    description='Tool to clean up expired sessions gracefully',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.3.0",
    ],
)
