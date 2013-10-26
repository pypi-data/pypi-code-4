from setuptools import setup, find_packages
 
setup(
    name='django-principals',
    version='0.1.4',
    description='A Django field for defining a principal instance.',
    author='Robert Moggach',
    author_email='rob@moggach.com',
    url='http://github.com/mogga/django-principals',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=['setuptools'],
)
