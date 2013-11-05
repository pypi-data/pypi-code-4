# fixcase.py - revert case changes in filenames
#
# Copyright 2008 Andrei Vermel <andrei.vermel@gmail.com>
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from mercurial.i18n import _
from mercurial.node import *
from mercurial import commands, cmdutil, hg, node, util, os

def fixcase(ui, repo, *pats, **opts):
    '''Revert case changes in filenames'''

    all = None
    node1, node2 = cmdutil.revpair(repo, None)

    files, matchfn, anypats = cmdutil.matchpats(repo, pats, opts)
    cwd = (pats and repo.getcwd()) or ''
    modified, added, removed, deleted, unknown, ignored, clean = [
        n for n in repo.status(node1=node1, node2=node2, files=files,
                             match=matchfn,
                             list_ignored=all,
                             list_clean=all)]
                             
    file_map={}                         
    for node in (node1, node2):
      m = repo.changectx(node).manifest()
      files = m.keys()
      for file in files:
      	file_map[file.lower()]=file
      	
      	
    for file in unknown:
      file_lower=file.lower()
      if file_lower in file_map:
      	ui.status(_('Reverted %s to %s\n') % (file, 
      	  file_map[file_lower]))
      	os.rename(file, file_map[file_lower])     	

cmdtable = {
    'fixcase':
        (fixcase,
         commands.walkopts,
        _('hg fixcase [SOURCE]')),
}
