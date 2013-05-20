#!/usr/bin/python

from distutils.core import setup

DISTUTILS_DEBUG = 1

setup(name='Pafy',
      version='0.1',
      description="Python API For YouTube, query and download YouTube content",
      long_description="""
Python API for YouTube
http://np1.github.io/pafy/
by nagev


Features:
---------

 - Download any stream for a particular video
 - Select best quality stream for download
 - Retreive metadata such as viewcount, duration, rating, author, thumbnail, keywords
 - Retrieve all availabe streams for a YouTube video (all resolutions and formats)
 - Retrieve the Download URL to download or stream the video
 - Small (< 150 lines of code) standalone, single importable module file.
 - Works with age-restricted videos and non-embeddable videos
 - No dependencies


Usage Examples:
---------------

Here is how to use the module in your own python code:

```python

>>> from pafy import Pafy
>>> url = "http://www.youtube.com/watch?v=dQw4w9WgXcQ"


    # create a video instance

>>> video = Pafy(url)


    # get certain attributes

>>> video.title
u'Rick Astley - Never Gonna Give You Up'

>>> video.rating
4.74645452989

>>> video.length
213

    # display video metadata

>>> print video
Title: Rick Astley - Never Gonna Give You Up
Author: RickAstleyVEVO
ID: dQw4w9WgXcQ
Duration: 00:03:33
Rating: 4.74645452989
Views: 63307745
Thumbnail: https://i1.ytimg.com/vi/dQw4w9WgXcQ/default.jpg
Keywords: Rick, Astley, Sony, BMG, Music, UK, Pop


    # show all formats for a video:

>>> streams = video.streams
>>> for s in streams:
>>>     print s.resolution, s.extension
480x854 webm
480x854 flv
360x640 webm
360x640 flv
360x640 mp4
240x400 flv
320x240 3gp
144x176 3gp
""",
      author="nagev",
      author_email="np1nagev@gmail.com",
      url="http://np1.github.io/pafy/",
      download_url="https://github.com/np1/pafy/tarball/master",
      py_modules=['pafy', 'example'],
      scripts=['example.py'],
      classifiers=[
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 2.6",
          "Topic :: Multimedia :: Sound/Audio :: Capture/Recording",
          "Topic :: Utilities",
          "Topic :: Multimedia :: Video",
          "Topic :: Internet :: WWW/HTTP"],

      package_data={"": ["CREDITS", "LICENSE", "README"]}
      )
