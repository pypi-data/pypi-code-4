# chardet's setup.py
from distutils.core import setup
setup(
    name = "bench",
    scripts = ['scripts/monitor.py'],
    requires = ['psutil'],
    version = "1.2",
    description = "Benchmark resources usage",
    author = "Xiaowei Zhan",
    author_email = "zhanxw@gmail.com",
    url = "http://zhanxw.com/bench",
    download_url = "http://zhanxw.com/bench",
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

Bench is able to monitor:
 - CPU time (user time, sys time, real time)
 - Memory usage (vms usage, rss usage)
 - Output to TSV(tab-delimited files)

Examples
--------

- Example 1: simple command

::
    
    > python ../monitor.py sleep 2
    
    PID	Prog	UsrTime	SysTime	RealTime	MaxVms	MaxRss	AvgVms	AvgRss	Path	Command
    14264	python	0.0	0.0	NA	NA	6728	NA	NA	/home/zhanxw/mycode/bench/bench	"python ../monitor.py sleep 2"

- Example 2: complex shell commands

::
    
    > python ../monitor.py -i 0.1 'sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait'
    
    PID	Prog	UsrTime	SysTime	RealTime	MaxVms	MaxRss	AvgVms	AvgRss	Path	Command
    13849	seq	0.48	0	0.4	7356416	634880	7356416.0	634880.0	/home/zhanxw/mycode/bench/bench	"seq 1000000"
    13845	python	0.54	0.0	NA	NA	6728	NA	NA	/home/zhanxw/mycode/bench/bench	"python ../monitor.py -i 0.1 sleep 2 & sleep 4 & seq 1000000 >/dev/null & wait"
    13847	sleep	0	0	1.9	7335936	368640	7335936.0	368640.0	/home/zhanxw/mycode/bench/bench	"sleep 2"


NOTE
----

 Shell (/bin/sh) are used to execute commands. It's a convenient feature with some shell exploit hazard.
 
 This version requires psutil.

Contact
-------

  Xiaowei Zhan<zhanxw[at]gmail.com>
  
"""
)
