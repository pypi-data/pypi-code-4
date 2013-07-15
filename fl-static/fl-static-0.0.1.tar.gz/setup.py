from setuptools import setup


if __name__ == '__main__':
    setup(
        name='fl-static',
        version='0.0.1',
        url='https://github.com/marksteve/fl-static',
        license='MIT',
        author='Mark Steve Samson',
        author_email='hello@marksteve.com',
        description='Serve production static files with Flask.',
        py_modules=['fl_static'],
        zip_safe=False,
        install_requires=[
            'flask',
            'static',
        ],
        platforms='any',
        classifiers=[
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    )
