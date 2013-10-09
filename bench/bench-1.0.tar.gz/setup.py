# chardet's setup.py
from distutils.core import setup
setup(
    name = "bench",
    packages = [""],
    scripts = ['scripts/monitor.py'],
    version = "1.0",
    description = "Benchmark resources usage",
    author = "Xiaowei Zhan",
    author_email = "zhanxw@gmail.com",
    url = "http://zhanxw.com/",
    download_url = "http://zhanxw.com/",
    keywords = ["benchmark", "process", "monitor"],
    classifiers = [
        "Programming Language :: Python",
	"Programming Language :: Python :: 2",
	"Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
	"Intended Audience :: Science/Research",
	"License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
	"Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Testing",
	"Topic :: System :: Monitoring",
        ],
    long_description = """\
Monitor Process Resources Usage
-------------------------------------

Monitor
 - CPU time (user time, sys time, real time)
 - Memory usage (vms usage, rss usage)
 - Output to TSV(tab-delimited files)
 
This version requires psutil.
"""
)
