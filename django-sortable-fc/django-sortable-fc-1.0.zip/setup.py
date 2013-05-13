from setuptools import setup, find_packages


setup(
    name='django-sortable-fc',
    version='1.0',
    description='An app to add drag-and-drop to admin to reorder instances of models.',
    author='Red Interactive Agency',
    author_email='geeks@ff0000.com',
    url='http://github.com/futurecolors/django-sortable/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)

