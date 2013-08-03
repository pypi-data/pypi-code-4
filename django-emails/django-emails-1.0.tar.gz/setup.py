from setuptools import setup, find_packages

version = '1.0'

setup(
    name='django-emails',
    version=version,
    description="Cron email sender.",
    keywords='django, admin, emails',
    author='Lubos Matl',
    author_email='matllubos@gmail.com',
    url='https://github.com/matllubos/django-emails',
    license='GPL',
    package_dir={'emails': 'emails'},
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: Czech',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    zip_safe=False
)