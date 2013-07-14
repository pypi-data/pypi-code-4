#!/usr/bin/python

from distutils.core import setup

setup(name="NBTParse",
      version='0.1.0', # NB: Until we hit 1.0, no alphas or betas
      author='Kevin Norris',
      author_email='nykevin.norris@gmail.com',
      url='https://bitbucket.org/NYKevin/nbtparse',
      packages=['nbtparse', 'nbtparse.syntax'],
      package_dir={'nbtparse': 'src'},
      classifiers=[
                   'Development Status :: 2 - Pre-Alpha',
                   'License :: OSI Approved :: BSD License',
                   'Topic :: Games/Entertainment',
                   'Topic :: Software Development :: Libraries',
                   'Intended Audience :: Developers',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   ],
      description="NBTParse is a Python package for parsing Named Binary Tags.",
      long_description="""NBTParse is a Python package for parsing Named Binary Tags.

        It follows the `unofficial specification`__ on the Minecraft Wiki.

        __ http://www.minecraftwiki.net/wiki/NBT_format

        NBTParse is intended to supplement the excellent NBTExplorer_, for
        scenarios where a high-level GUI is inconvenient or cumbersome.

        .. _NBTExplorer: http://www.minecraftforum.net/topic/840677-nbtexplorer-nbt-editor-for-windows-and-mac/

        Support for interaction with more complex types of data, such as
        Minecraft chunks, regions, and worlds, is planned but not implemented.
        """
    )

