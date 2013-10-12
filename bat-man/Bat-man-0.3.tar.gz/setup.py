from setuptools import setup

def long_desc():
    with open("README.rst") as f:
        return f.read()

setup(
    name="Bat-man",
    description="A YouTube batch downloader and converter.",
    long_description=long_desc(),
    version="0.3",
    author="ElegantMonkey",
    author_email="ramon100.black@gmail.com",
    url="http://github.com/ElegantMonkey/Bat-man",
    packages=["batman", "batman.codec_interface"],
    include_package_data=True,
    entry_points={
        "gui_scripts": ["bat-man=batman.gtk_batch_downloader:main"]
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: End Users/Desktop',
        'Environment :: X11 Applications :: GTK',
        'Development Status :: 2 - Pre-Alpha',
    ]
)

