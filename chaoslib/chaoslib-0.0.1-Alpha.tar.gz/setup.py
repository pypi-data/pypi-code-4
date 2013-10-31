from setuptools import setup

setup(name='chaoslib',
      version='0.0.1-Alpha',
      description='Sorting library for chaotic sorting.',
      url='https://github.com/dansun/chaoslib',
      download_url='https://github.com/dansun/chaoslib',
      author='Daniel Sundberg',
      author_email='daniel@danielsundberg.nu',
      license='GNU v2',
      packages=['chaoslib'],
      install_requires=['randomdotorg'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False,
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"],
      long_description = """\
      -------------------------------------------------------------------
         _________ .__                        .____    ._____.    
         \_   ___ \|  |__ _____    ____  _____|    |   |__\_ |__  
         /    \  \/|  |  \\__  \  /  _ \/  ___/    |   |  || __ \ 
         \     \___|   Y  \/ __ \(  <_> )___ \|    |___|  || \_\ \
          \______  /___|  (____  /\____/____  >_______ \__||___  /
                 \/     \/     \/           \/        \/       \/ 
      -------------------------------------------------------------------
      
      Sorts a list of numbers by randomly mutating the list.
      chaoslib.sort([3,1,2]) returns [3,2,1]

      """


      )
