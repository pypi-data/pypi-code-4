#!/home/bill/py3/.virtualenvs/pytest/bin/python
# EASY-INSTALL-ENTRY-SCRIPT: 'Csys==1.25','console_scripts','csgetcfg.py'
__requires__ = 'Csys==1.25'
import sys
from pkg_resources import load_entry_point

sys.exit(
   load_entry_point('Csys==1.25', 'console_scripts', 'csgetcfg.py')()
)
