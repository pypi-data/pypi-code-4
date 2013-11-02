from setuptools import setup, find_packages

setup(
        name='mp3fm',
        version='1.0.4',
        author='Akshit Agarwal',
        author_email='akshit.jiit@gmail.com',
        url='https://github.com/Aki92/mp3fm',
        packages=find_packages(),
        entry_points = {
            'console_scripts': ['mp3fm = mp3fm.mp3fm:main']
                        },
        install_requires=['easygui', 'mutagen', 'musicbrainzngs'],
        license='MIT',
        description='''I believe that for Music Lovers its a big problem to keep songs organized into folders, so here comes a simple solution to that problem. Just run the app and it will Pack the Songs into folders according to the option you choose from Album(Movie)/Artist/Year/Comments/Title/Duration.''',
        long_description=open('README.rst').read(),
        classifiers=["Environment :: Console", "Topic :: Multimedia"],

    )

