import dcors

from setuptools import setup, find_packages


setup(
    name='django-dcors',
    version=dcors.__version__,
    description="Django middleware for adding CORS HTTP headers.",
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=['django', 'CORS'],
    author='Prasanth Nair',
    author_email='prasanth.n@outlook.com',
    url='http://github.com/prasanthn/django-dcors',
    license='MIT',
    packages=find_packages(exclude=['docs']),
    include_package_data=True,
)
