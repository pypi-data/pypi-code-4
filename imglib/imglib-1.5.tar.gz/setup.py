from setuptools import setup
#python setup.py sdist bdist upload
setup(
    name='imglib',
    version="1.5",
    description = 'search a sub image from a parent image',
    author = 'baohongbin',
    author_email = 'hongbin.bao@gmail.com',
    license = 'MIT',
    keywords     = 'python opencv binding to search sub image',
    platforms    = 'Linux',
    long_description = """\
find a sub image from a parent image and calculate the center point (X,Y) coordinate\n
usage:\n
>>> from imglib.imgcomparison import isMatch, getMatchedCenterOffset, isMatchFromUrl\n
>>> isMatch(path_of_subimg,path_of_parentimg , threshold=0.01)\n""",
    packages = ['imglib', 'tests'],
    classifiers=[
        "Development Status :: 3 - Alpha",
    ],
)
