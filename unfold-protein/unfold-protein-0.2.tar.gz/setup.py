# Copyright

"unfold-protein: velocity clamp protein unfolding experiment control"

from distutils.core import setup

from unfold_protein import __version__


package_name = 'unfold-protein'

setup(name=package_name,
      version=__version__,
      maintainer='W. Trevor King',
      maintainer_email='wking@tremily.us',
      url='http://blog.tremily.us/posts/{}/'.format(package_name),
      download_url='http://git.tremily.us/?p={}.git;a=snapshot;h={};sf=tgz'.format(package_name, __version__),
      license='GNU General Public License v3 (GPLv3)',
      platforms=['all'],
      description=__doc__,
      long_description=open('README', 'r').read(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      packages=[package_name.replace('-', '_')],
      scripts=['unfold.py', 'plot-unfold.py'],
      provides=['{} ({})'.format(package_name.replace('-', '_'), __version__)],
      requires=['pyafm (>= 0.5)'],
      )
