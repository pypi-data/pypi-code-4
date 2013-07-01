from setuptools import setup, find_packages

version = 0.2

setup(
    name="anybox.funkload.openerp",
    version=version,
    author="Georges Racinet",
    author_email="gracinet@anybox.fr",
    description="Base classes for functional and load testing of OpenERP "
                "with Funkload",
    license="GPLv3",
    long_description=open('README.txt').read() + open('CHANGES.txt').read(),
    url="https://launchpad.net/anybox.funkload.openerp",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    namespace_packages=['anybox', 'anybox.funkload'],
    install_requires=['setuptools', 'funkload', 'simplejson'],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 "
            "or later (GPLv3+)",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Benchmark",
    ],
    entry_points={},
)
