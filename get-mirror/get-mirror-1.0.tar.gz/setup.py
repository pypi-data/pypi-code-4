from setuptools import setup

setup(
    name='get-mirror',
    version="1.0",

    description='',
    long_description = '',
    author='CJ',
    author_email='weicongju@gmail.com',
    license='BSD',
    url = 'http://github.com/imcj/get-mirror',
    zip_safe = False,

    packages=['get_mirror'],
    entry_points="""
[console_scripts]
get-mirror=get_mirror:__main__
""",
    classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Unix',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.5',
          'Programming Language :: Python :: 2.6',
          'Topic :: Software Development',
          'Topic :: Software Development :: Build Tools',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: System :: Software Distribution',
          'Topic :: System :: Systems Administration',
    ],

)
