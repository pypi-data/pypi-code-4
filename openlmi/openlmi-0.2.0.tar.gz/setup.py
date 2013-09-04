from setuptools import setup
setup(
    name='openlmi',
    description='OpenLMI python providers',
    author='Michal Minar',
    author_email='miminar@redhat.com',
    url='https://fedorahosted.org/openlmi/',
    version='0.2.0',
    license='LGPLv2+',
    namespace_packages = ['lmi'],
    packages = ['lmi', 'lmi.base', 'lmi.providers'],
    classifiers=[
        'License :: OSI Approved :: GNU Lesser General Public License'
            ' v2 or later (LGPLv2+)',
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Systems Administration',
        ]
    )
