from distutils.core import setup


setup(
    name="ssvm",
    version="0.22",
    description="",
    packages=['ssvm',],
    long_description=open('README.txt').read(),
    author="Yuh-Jye Lee",
    author_email="yuh-jye@mail.ntust.edu.tw",
    maintainer="Zi-Wen Gui",
    maintainer_email="evan176@hotmail.com",

    url="http://dmlab8.csie.ntust.edu.tw/",

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    zip_safe=False,
)
