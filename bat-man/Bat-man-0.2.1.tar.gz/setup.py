from setuptools import setup

setup(
    name="Bat-man",
    description="YouTube batch downloader - to MP3 files.",
    version="0.2.1",
    author="ElegantMonkey",
    author_email="ramon100.black@gmail.com",
    url="http://github.com/ElegantMonkey/Bat-man",
    packages=["batman"],
    include_package_data=True,
    entry_points={
        "gui_scripts": ["bat-man=batman.gtk_batch_downloader:main"]
    }
)

