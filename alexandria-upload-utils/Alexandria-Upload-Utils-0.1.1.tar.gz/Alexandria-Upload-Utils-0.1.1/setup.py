from setuptools import setup

setup(
    name='Alexandria-Upload-Utils',
    version='0.1.1',
    url='https://github.com/tedw4rd/alexandria-upload-utils/',
    license='MIT',
    author='Ted Aronson',
    author_email='ted.aronson@gmail.com',
    description='Easy uploads to an Alexandria build archive',
    long_description=__doc__,
    data_files=[],
    py_modules=["alexandria_upload"],
    platforms='any',
    install_requires=[
        'requests >= 2.0.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
