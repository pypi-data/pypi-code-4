from setuptools import setup

setup(
    name='django-doccloud',
    version='0.5.0',
    description='Provides a reusable document app to add and edit files hosted by DocumentCloud',
    author='Shane Shifflett',
    author_email='shifflett.shane@gmail.com',
    url='http://github.com/BayCitizen/django-doccloud/',
    packages=[
        'doccloud',
    ],
    package_data={'doccloud': ['templates/*.html']},
    install_requires=[
        'python-documentcloud',
	'django-extensions'
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
