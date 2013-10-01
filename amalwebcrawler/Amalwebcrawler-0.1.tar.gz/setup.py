#  setuptools file  By Amal

# --------------------------------
from setuptools import setup , find_packages
setup( name = "Amalwebcrawler",
        version = "0.1",
        packages =find_packages(),
        scripts = ['Amal_crawler'],
        install_requires=['BeautifulSoup'],
        package_data = { 'pymycraawler': [' '], }, 
        author = "Amal Roumi Suliman",
        author_email = "roumia@gmail.com",
        description = "Web crawler in Python ",
        license  = "GNU GPLv3",
        keywords = "web_crawler ,MSWL, web_spider, python ",
        url = "https://github.com/Roumia/mswl-dt",
        long_description = " Web crawler in Python ,assignments for \
                             Development Tools one of the subject in MSWL,URJC\
                             that get the current version of a web pagSpider to\
                             track the updates of a web page",
        download_url = "", )
