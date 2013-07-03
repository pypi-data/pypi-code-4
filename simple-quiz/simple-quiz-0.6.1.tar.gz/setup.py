from setuptools import setup, find_packages

setup( name='simple-quiz',
    version = '0.6.1',
    description = 'A simple, multiple-guess Quiz app',
    author = 'Curtis Maloney',
    author_email = 'curtis@tinbrain.net',
    url = 'http://bitbucket.org/funkybob/simple-quiz/',
    keywords = ['django', 'quiz',],
    packages = find_packages(),
    include_package_data = True,
    package_data = {
        'quiz': ['templates/admin/quiz/sitting/*',],
    },
    zip_safe = False,
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = [
        'Django>=1.2',
    ]
)
