from distutils.core import setup

setup(
    name='send_email_message',
    version='0.1.2',
    description='Very simple and unicode friendly way to send email message from Python code.',
    long_description='''
Usage::

    sudo pip install send_email_message
    from send_email_message import send_email_message

    email_config = dict(
        host='smtp.gmail.com',
        port=587,
        tls=True, // Or ssl=True with another port.
        user='admin@example.com',
        password='password',
        from_name='Example Site',
        # Default: encoding='utf-8'
    )

    send_email_message(to='denisr@denisr.com', subject='Example News', text='Please see http://example.com/', **email_config)

''',
    url='https://github.com/denis-ryzhkov/send_email_message',
    author='Denis Ryzhkov',
    author_email='denisr@denisr.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    py_modules=['send_email_message'],
)
