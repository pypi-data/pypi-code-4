"""hgpushsvn must be run in a repository created by hgimportsvn. It pushes
local Mercurial changesets one by one or optionally collapsed into a single
commit back to the SVN repository.

"""

import codecs
import os
import stat
import sys
import re
from optparse import OptionParser
import copy

from hgsvn import ui
from hgsvn.common import (
    run_hg, run_svn, hg_switch_branch, hgsvn_private_dir,
    check_for_applied_patches, get_encoding,
    check_branchmap,
    load_hgsvn_branches_map,
    get_parents_from_hg, get_branch_from_hg, get_svn_rev_from_hg
    , get_branchinfo_from_hg, svn_base_of_branch
    , hg_force_switch_branch, hg_is_clean
    , load_svnignores, is_ignore4svn, save_svnignores, append_ignore4svn
    , get_hg_cset, strip_hg_rev
    , get_svn_rev_of_hgbranch
    )
from hgsvn.errors import ExternalCommandFailed, EmptySVNLog, HgSVNError
from hgsvn.run.common import run_parser, display_parser_error
from hgsvn.run.common import locked_main
from hgsvn.svnclient import (get_svn_info, get_svn_status
    , svn_switch_to
    , svn_resolve_all
    )

svn_branch = ""
repos_url   = ""

def IsDebug():
    return (ui._level >= ui.DEBUG)


def map_svn_rev_to_hg(svn_rev, hg_rev="tip", local=False):
    """
    Record the mapping from an SVN revision number and an hg revision (default "tip").
    """
    args = ["tag"]
    if local:
        args.append("-l")
    args.extend(["-r", strip_hg_rev(hg_rev), "svn.%d" % svn_rev])
    run_hg(args)

def get_hg_revs(first_rev, svn_branch, last_rev="tip"):
    """
    Get a chronological list of revisions (changeset IDs) between the two
    revisions (included).
    """
    args = ["log", "--template", r'{rev}:{node|short}\n', "-b", svn_branch,
            '--limit', '1000', '--follow',
            "-r", "%s::%s" % (strip_hg_rev(first_rev),
                             strip_hg_rev(last_rev))]
    out = run_hg(args)
    return [strip_hg_rev(s) for s in out.splitlines()]

def get_hg_revs_with_graph(first_rev, svn_branch, last_rev="tip"):
    """
    Get a chronological list of revisions (changeset IDs) between the two
    revisions (included).
    tree contains nodes description as [parents, childs]
    """
    args = ["log", "--template", r'{rev}:{node|short};{parents};{children}\n', "-b", svn_branch,
            '--limit', '1000', '--follow',
            "-r", "%s::%s" % (strip_hg_rev(first_rev),
                             strip_hg_rev(last_rev))]
    out = run_hg(args)
    lines = [s.strip() for s in out.splitlines()]
    revs = list()
    hg_tree = dict()
    parents = []
    childs = []
    for line in lines:
        (rev, parent, child) = re.split(";",line)
        rev_no, rev_id = re.split(":", rev)
        revs.append(rev_id) #strip_hg_rev(rev));
        parents = re.split(" ",parent.strip());
        childs = re.split(" ",child.strip());
        hg_tree[rev_id] = [parents, childs, rev_no]
    if IsDebug():
        print "hg have hystory tree:"
        for node in hg_tree.items():
            print node
    return revs, hg_tree

def is_anonimous_branch_head(rev, hg_tree):
    """
    checks chat revision have more than one child in branch
    """
    if not hg_tree.has_key(rev):
        return False
    childs = hg_tree[rev][1]
    if len(childs) <= 1:
        return False
    ChildsInTree = 0
    for s in childs:
        if hg_tree.has_key(strip_hg_rev(s)):
            ChildsInTree = ChildsInTree+1
    return (ChildsInTree > 1)

def get_pairs(l):
    """
    Given a list, return a list of consecutive pairs of values.
    """
    return [(l[i], l[i+1]) for i in xrange(len(l) - 1)]

def get_hg_changes(rev_string):
    """
    Get paths of changed files from a previous revision.
    Returns a tuple of (added files, removed files, modified files, copied files)
    Copied files are dict of (dest=>src), others are lists.
    """
    args = ["st", "-armC", "--rev", rev_string]
    out = run_hg(args, output_is_locale_encoding=True)
    added = []
    removed = []
    modified = []
    copied = {}
    skipnext = False
    for line in out.splitlines():
        st = line[0]
        path = line[2:]
        if (is_ignore4svn(path)): continue
        if st == 'A':
            added.append(path)
            lastadded=path
        elif st == 'R':
            removed.append(path)
        elif st == 'M':
            modified.append(path)
        elif st == ' ':
            added.remove(lastadded)
            copied[lastadded] = path
    #print "added:", added
    #print "removed:", removed
    #print "modified:", modified
    return added, removed, modified, copied

def cleanup_svn_type(files, svn_status=None, state='unversioned'):
    """
        removes svn:<state> entry from files, status=<None> - removes all recognised in svn entries
    """
    if svn_status is None:
        svn_status = get_svn_status(".")
    stated = list()
    for entry in svn_status:
        if (entry['path'] in files):
          if (state is None) or (entry['type'] == state):
            files.remove(entry['path'])
            stated.append(entry['path'])
    return files, stated

def cleanup_svn_status(files, svn_status=None, state='unversioned'):
    """
        removes svn:<state> entry from files, status=<None> - removes all recognised in svn entries
    """
    if svn_status is None:
        svn_status = get_svn_status(".")
    stated = list()
    for entry in svn_status:
        if (entry['path'] in files):
          if (state is None) or (entry['status'] == state):
            files.remove(entry['path'])
            stated.append(entry['path'])
    return files, stated

def cleanup_svn_notatype(files, svn_status=None, state='unversioned'):
    """
        leaves only svn:<state> entry in files, status=<None> - leaves all recognised in svn entries
    """
    if svn_status is None:
        svn_status = get_svn_status(".")
    nostatedfile = list()
    statedfile = list()
    for entry in svn_status:
        if (entry['path'] in files):
          files.remove(entry['path'])
          if (state is None) or (entry['type'] == state):
            statedfile.append(entry['path'])
          else:
            nostatedfile.append(entry['path'])
    nostatedfile.extend(files)
    del files[:]
    files.extend(statedfile)
    return files, nostatedfile

def cleanup_svn_versioned(files, svn_status=None):
    files, verfiles = cleanup_svn_notatype(files, svn_status, 'unversioned')
    verfiles, absentfiles = cleanup_svn_notatype(verfiles, svn_status, None)
    files.extend(absentfiles)
    return files, verfiles

def cleanup_svn_unversioned(files, use_svn_status=None):
    files, unverfiles = cleanup_svn_type(files, use_svn_status, 'unversioned')
    files, absentfiles = cleanup_svn_notatype(files, use_svn_status, None)
    unverfiles.extend(absentfiles)
    return files, unverfiles

def svn_unversioned(files, svn_status = None):
    if svn_status is None:
        svn_status = get_svn_status(".")
    res = list([])
    for entry in svn_status:
        if(entry['type'] == 'unversioned') and entry['path'] in files:
            res.append(entry['path'])
    return res

def get_ordered_dirs(l):
    if l is None :
        return []
    """
    Given a list of relative file paths, return an ordered list of dirs such that
    creating those dirs creates the directory structure necessary to hold those files.
    """
    dirs = set()
    for path in l:
        while True:
            if not path :
                break
            path = os.path.dirname(path)
            if not path or path in dirs:
                break
            dirs.add(path)
    return list(sorted(dirs))

def get_hg_csets_description(start_rev, end_rev):
    """Get description of a given changeset range."""
    return run_hg(["log", "--template", r"{desc|strip}\n", "--follow"
                    , "--branch", svn_branch
                    , "--rev", start_rev+":"+end_rev, "--prune", start_rev])

def get_hg_cset_description(rev_string):
    """Get description of a given changeset."""
    return run_hg(["log", "--template", "{desc|strip}", "-r", rev_string])

def get_hg_log(start_rev, end_rev):
    """Get log messages for given changeset range."""

    log_args=["log", "--verbose", "--follow", "--rev", start_rev+"::"+end_rev, "--prune", start_rev]
    return run_hg(log_args)

def get_svn_subdirs(top_dir):
    """
    Given the top directory of a working copy, get the list of subdirectories
    (relative to the top directory) tracked by SVN.
    """
    subdirs = []
    def _walk_subdir(d):
        svn_dir = os.path.join(top_dir, d, ".svn")
        if os.path.exists(svn_dir) and os.path.isdir(svn_dir):
            subdirs.append(d)
            for f in os.listdir(os.path.join(top_dir, d)):
                d2 = os.path.join(d, f)
                if f != ".svn" and os.path.isdir(os.path.join(top_dir, d2)):
                    _walk_subdir(d2)
    _walk_subdir(".")
    return subdirs

def strip_nested_removes(targets):
    """Strip files within removed folders and return a cleaned up list."""
    # We're going a safe way here: "svn info" fails on items within removed
    # dirs.
    clean_targets = []
    for target in targets:
        try:
            run_svn(['info', '--xml', target], mask_atsign=True)
        except ExternalCommandFailed, err:
            ui.status(str(err), level=ui.DEBUG)
            continue
        clean_targets.append(target)
    return clean_targets

def adjust_executable_property(files, svn_status = None):
    execflags = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    svn_map = {}
    check_files = files

    if svn_status is not None:
        #if have status cached, then use it to filter only files that have props
        check_files = []
        for entry in svn_status:
            if (entry['path'] in files):
                if (entry['props'] != "none"):
                    check_files.append(entry['path'])
        if IsDebug():
            print "adjust_executable_property: select files with props:%s" % check_files

    for fname in check_files:
        if run_svn(['propget', 'svn:executable', fname],
                   mask_atsign=True).strip():
            svn_map[fname] = True
        else:
            svn_map[fname] = False
    for fname in check_files:
        m = os.stat(fname).st_mode & 0777
        is_exec = bool(m & execflags)
        actual_exec = svn_map.has_key(fname);
        if actual_exec:
              actual_exec = svn_map[fname];
        if is_exec and not actual_exec:
            run_svn(['propset', 'svn:executable', 'ON', fname],
                    mask_atsign=True)
        elif not is_exec and actual_exec:
            run_svn(['propdel', 'svn:executable', fname], mask_atsign=True)

def do_svn_copy(src, dest):
    """
    Call Svn copy command to record copying file src to file dest.
    If src is present then backup src before other tasks.
    Before issuing copy command move dest to src and remove src after
    """
    backup_src = ''
    if os.path.exists(src):
        backup_src = os.path.join(hgsvn_private_dir, "hgpushsvn_backup.tmp")
        os.rename(src, backup_src)

    try:
        try:
            # We assume that src is cotrolled by svn
            os.rename(dest, src)

            # Create svn subdirectories if needed
            # We know that subdirectories themselves are present
            # as dest is present
            pattern = re.compile(r"[/\\]")
            pos = 0
            while(True):
                match = pattern.search(dest, pos + 1)
                if match == None:
                    break

                pos = match.start()
                try:
                    run_svn(['add', '--depth=empty'], [dest[:pos]],
                            mask_atsign=True)
                except (ExternalCommandFailed), e:
                    if not str(e).find("is already under version control") > 0:
                        raise
                pos = match.end() - 1

            # Do the copy itself
            run_svn(['copy', src, dest], mask_atsign=True)
        except ExternalCommandFailed:
            # Revert rename
            os.rename(src, dest)
            raise
    finally:
        if os.path.isfile(src):
            os.remove(src)

        if(backup_src):
            os.rename(backup_src, src)

def hg_push_svn(start_rev, end_rev, edit, username, password, cache, options, use_svn_wc = False):
    """
    Commit the changes between two hg revisions into the SVN repository.
    Returns the SVN revision object, or None if nothing needed checking in.
    use_svn_wc - prevents reverting wc state to start_rev, and thus accepts changes that 
                prepared here
    """

    # Before replicating changes revert directory to previous state...
    run_hg(['revert', '--all', '--no-backup', '-r', end_rev])

    if not use_svn_wc:
        # ... and restore .svn directories, if we lost some of them due to removes
        run_svn(['revert', '--recursive', '.'])

    # Do the rest over up-to-date working copy
    # Issue 94 - moved this line to prevent do_svn_copy crashing when its not the first changeset
    run_hg(["up", "-C", end_rev])
    
    added, removed, modified, copied = get_hg_changes(start_rev+':'+end_rev)

    svn_status_cache = get_svn_status(".")

    added, modified_add = cleanup_svn_status(added, svn_status_cache, 'modified')
    added, alredy_add = cleanup_svn_status(added, svn_status_cache, 'normal')
    cleanup_svn_unversioned(removed, svn_status_cache)

    modified, unversioned_change  = cleanup_svn_unversioned(modified, svn_status_cache)
    if unversioned_change:
        print "this changes %s unverioned in svn" % unversioned_change
        if options.on_noversioned_change == "add" :
            added.extend(unversioned_change)
        elif options.on_noversioned_change == "skip":
            unversioned_change = None   #this is dummy - for skip choose nothig to do
        else:
            raise HgSVNError("unckonwn action %s for unversioned changes" % options.on_noversioned_change)

    if modified_add:
        ui.status("this added files alredy versioned in svn:%s"
                  " just state it as modify" % modified_add)
        modified.extend(modified_add)

    cleanup_svn_versioned(added, svn_status_cache)  #drop alredy versioned nodes from addition

    if alredy_add:
        ui.status("this added %s alredy verioned in svn" % alredy_add)
        modified.extend(alredy_add)    #and place them to modified

    # Record copyies into svn
    for dest, src in copied.iteritems():
        do_svn_copy(src,dest)

    # Add new files and dirs
    if added:
        svnadd = list(added)
        cleanup_svn_status(svnadd, svn_status_cache, 'added') #not add alredy added filess
        if svnadd:
            bulk_args = cleanup_svn_versioned(get_ordered_dirs(svnadd), svn_status_cache)[0]
            bulk_args += svnadd
            run_svn(["add", "--depth=empty"], bulk_args, mask_atsign=True)

    if IsDebug():
        print "svn to add:", added
        print "svn to remov:", removed
        print "svn to modify:", modified

    # Remove old files and empty dirs
    if removed:
        svnremove = list(removed)
        cleanup_svn_type(svnremove, svn_status_cache, 'removed') #drop alredy removed nodes from removing
        empty_dirs = [d for d in reversed(get_ordered_dirs(svnremove))
                      if not run_hg(["st", "-c", "%s" %d])]
        # When running "svn rm" all files within removed folders needs to
        # be removed from "removed". Otherwise "svn rm" will fail. For example
        # instead of "svn rm foo/bar foo" it should be "svn rm foo".
        # See issue15.
        svn_removed = strip_nested_removes(svnremove + empty_dirs)
        if svn_removed:
            run_svn(["rm"], svn_removed, mask_atsign=True)
    if added or removed or modified or copied:
        svn_sep_line = "--This line, and those below, will be ignored--\n"
        adjust_executable_property(added+modified, svn_status_cache)  # issue24
        description = get_hg_csets_description(start_rev, end_rev)
        fname = os.path.join(hgsvn_private_dir, 'commit-%s.txt' % end_rev)
        lines = description.splitlines()+[""]
        lines.append(svn_sep_line)
        lines.append("To cancel commit just delete text in top message part")
        lines.append("")
        lines.append("Changes to be committed into svn:")
        for item in svn_status_cache:
            if item['type'] != 'unversioned':
                lines.extend( "%s       %s" % (item['type'], item['path']))
        lines.append("")
        lines.append(("These changes are produced from the following "
                      "Hg changesets:"))
        lines.extend(get_hg_log(start_rev, end_rev).splitlines())
        f = codecs.open(fname, "wb", "utf-8")
        f.write(os.linesep.join(lines))
        f.close()

        try:
            if edit:
                editor=(os.environ.get("HGEDITOR") or
                        os.environ.get("SVNEDITOR") or
                        os.environ.get("VISUAL") or
                        os.environ.get("EDITOR", "vi"))

                rc = os.system("%s \"%s\"" % (editor, fname) )
                if(rc):
                    raise ExternalCommandFailed("Can't launch editor")

                empty = True

                f=open(fname, "r")
                for line in f:
                    if(line == svn_sep_line):
                        break

                    if(line.strip() != ""):
                        empty = False
                        break
                f.close()

                if(empty):
                    raise EmptySVNLog("Commit cancelled by user\n")

            svn_rev = None
            svn_commands = ["commit", "-F", fname, "--encoding", "utf-8" ]#get_encoding()]
            if username is not None:
                svn_commands += ["--username", username]
            if password is not None:
                svn_commands += ["--password", password]
            if cache:
                svn_commands.append("--no-auth-cache")
            out = run_svn(svn_commands)

            if IsDebug():
                print "svn commit:%s" % out
            
            svn_rev = None
            try:
              outlines = out.splitlines(True)
              outlines.reverse()
              for line in outlines:
                # one of the last lines holds the revision.
                # The previous approach to set LC_ALL to C and search
                # for "Committed revision XXX" doesn't work since
                # svn is unable to convert filenames containing special
                # chars:
                # http://svnbook.red-bean.com/en/1.2/svn.advanced.l10n.html
                match = re.search("(\d+)", line)
                if match:
                    svn_rev = int(match.group(1))
                    break
            finally:
              if svn_rev is None:
                #if retrieve revision from commit report fails? do it with additional svn request
                svn_info = get_svn_info(".")
                svn_rev = svn_info["revision"]


            return svn_rev
        finally:
            # Exceptions are handled by main().
            os.remove(fname)
        return None
    else:
        print "*", "svn: nothing to do"
        return None

def svn_merge_2wc(rev_number, svn_base, svnacception = "working"):
    args = ["merge","--non-interactive","--accept=%s"%svnacception]
    if rev_number is not None:
        svn_base += '@%d'%rev_number
    ui.status("merging %s" % (svn_base), level=ui.VERBOSE)
    svn_base = svn_base.lstrip('/\\');
    args += [repos_url +'/'+svn_base]
    return run_svn(args)

def svn_merge_range_2wc(svn_base, rev_first, rev_last, svnacception = "mine-conflict"):
    args = ["merge","--non-interactive","--accept=%s"%svnacception]
    svn_base = svn_base.lstrip('/\\');
    svn_target = svn_base;
    svn_range = '%d:%d'%(rev_first, rev_last)
    ui.status("merging %s with %s" % (svn_target, svn_range), level=ui.VERBOSE)
    try:
        result = run_svn(args + ["-r", svn_range , repos_url +'/'+svn_target])
    except:
        ui.status("failed merge revrange, so try merge different tree " % (svn_target, svn_range), level=ui.ALERT)
        svn_revert_all();
        svn_first = '%s@%d'%(svn_base, rev_first);
        svn_last  = '%s@%d'%(svn_base, rev_last);
        ui.status("merging %s : %s" % (svn_first, svn_last), level=ui.VERBOSE)
        args += ["--ignore-ancestry"]
        result = run_svn(args + [repos_url +'/'+svn_first, repos_url +'/'+svn_last])
    return result 

def hg_sync_merge_svn(start_rev, rev, hg_tree, svn_branch, options):
    #   start_rev - parent rev on wich merges rev
    #   rev - mergepoint rev
    #   check all parents for branch name, and try to push one branches if can
    #   after all branches complete, merge svn work copy and resolves it for hg_push_svn
    
    # Before replicating changes revert directory to previous state...
    run_hg(['revert', '--all', '--no-backup', '-r', start_rev])
    # ... and restore .svn directories, if we lost some of them due to removes
    run_svn(['revert', '--recursive', '.'])

    parents = hg_tree[rev][0]
    if len(parents) <= 1:
        return True

    if IsDebug():
        print "merge for parents:%s"%parents
    branches = dict()
    
    for s in parents:
        r = strip_hg_rev(s)
        branchname = svn_branch
        BranchSVNRev = None
        if not hg_tree.has_key(r):
            branchname, BranchSVNRev = get_branchinfo_from_hg(s)
 
        headinfo = [s,BranchSVNRev]
        if branches.has_key(branchname):
            branches[branchname].extend(headinfo)
        else:
            branches[branchname] = [headinfo]
    if IsDebug():
        print "merge have branches:"
        for node in branches.items():
            print node

    for bp in branches.itervalues():
        #check that all parent is one from its branch
        if len(bp) > 1:
            ui.status("Mercurial repository rev:%s have multiple parents %s of branch %s,"
                      " cant distinguish how to push it" % (s, bp, svn_branch) 
                     )
            return False

    if branches.has_key(svn_branch):
        del branches[svn_branch]
    
    branch_affected =False
    merge_svn_revs = []
    branch_switched = False
    current_branch = svn_branch
    for node in branches.items():
        use_branch = node[0]
        head = node[1][0]
        hg_parent = head[0]
        svn_parent = head[1]
        svn_base = svn_base_of_branch(use_branch)
        if svn_base is None:
                ui.status("rev:%s need push for parent %s of branch %s, that is uncknown location in svn" % (rev, hg_parent, use_branch ))
                return False
        if svn_parent is None:
            #there is no svn tag attached
            # this is unversioned head, so its branch should be pushed for one rev
            ui.status("rev:%s need push for parent %s of branch hg:%s svn:%s" % (rev, hg_parent, use_branch, svn_base ))
            current_branch = use_branch
            branch_switched = True
            #first switch svn to desired branch. after that, switch hg to ones - this provides clean hg state
            #   that is requred by real_main
            svn_switch_to(repos_url +'/'+svn_base, ignore_ancetry=True) #clean=True
            if not hg_force_switch_branch(use_branch):
                if not options.force:
                    raise HgSVNError("failed to switch to branch <%s> for push" % use_branch)
            use_options = copy.deepcopy(options)
            use_options.svn_branch = use_branch
            use_options.tip_rev = hg_parent
            try:
                if real_main(use_options, [], clean=False ) != 0:
                    raise
                svn_parent = get_svn_rev_from_hg(strip_hg_rev(hg_parent))
                merge_svn_revs.append([svn_parent, hg_parent, use_branch, svn_base])
            except:
                if not options.force:
                    raise HgSVNError("failed to push branch <%s>" % use_branch)
        else:
            merge_svn_revs.append([svn_parent, hg_parent, use_branch, svn_base])


    if current_branch != svn_branch: #branch_switched:
        ui.status("switch from branch %s back to %s " % (current_branch, svn_branch))
        svn_base = svn_base_of_branch(svn_branch)
        svn_switch_to(repos_url +'/'+svn_base, clean=True, ignore_ancetry=True)
        hg_force_switch_branch(svn_branch, start_rev)

    if len(merge_svn_revs) == 0:
        return options.force

    #now all parents is ok, lets merge it
    #do the merge in svn rev order
    if len(merge_svn_revs) > 1:
        print "sorting list %s"% merge_svn_revs
        merge_svn_revs.sort(key=lambda rev_node: rev_node[0])
    for elem in merge_svn_revs:
        try:
            svn_merge_2wc(elem[0], elem[3], svnacception = options.svnacception)
        except:
            #since svn normal merge fails? try to merge revs range
            #try to find last common incoming rev
            ui.status("fail to merge svn:%s"%(elem[0]), loglevel = ui.ALERT);

            args = ["log", "--template", r'{rev}:{node|short}\n',
                    "-r", "last(ancestors(%s) and branchpoint() and branch(\"%s\"))" % (strip_hg_rev(start_rev), elem[2])
                    ]
            last_branch_incoming_rev = run_hg(args)
            if len(last_branch_incoming_rev) <= 0 :
                # there is no merge-in from desired branch, therefore merge from it`s base rev
                args = ["log", "--template", r'{rev}:{node|short}\n',
                        "-r", "first(branch(%s))" % (elem[2])
                        ]
                last_branch_incoming_rev = run_hg(args)
                if len(last_branch_incoming_rev) <= 0 :
                    return options.force

            ui.status("try merge revs range from hg:%s"%(last_branch_incoming_rev), level=ui.VERBOSE);
            last_branch_incoming_svnrev = get_svn_rev_from_hg( get_hg_cset(last_branch_incoming_rev) );
            if (last_branch_incoming_svnrev is None):
                ui.status("hg:%s not synched 2 svn"%(last_branch_incoming_rev), level=ui.WARNING);
                return options.force

            ui.status("try merge revs range from svn:%s to svn:%s"%(last_branch_incoming_svnrev, elem[0]), level=ui.VERBOSE);
            svn_merge_range_2wc(elem[3], last_branch_incoming_svnrev, elem[0], svnacception = options.svnacception)

    #now resolve all conflicts
    svn_resolve_all()
    return True

def real_main(options, args, clean = True):
    global hgsvn_branchmap
    global repos_url

    if run_hg(["st", "-S", "-m"]):
        print ("There are uncommitted changes possibly in subrepos. Either commit them or put "
               "them aside before running hgpushsvn.")
        return 1
    if check_for_applied_patches():
        print ("There are applied mq patches. Put them aside before "
               "running hgpushsvn.")
        return 1

    orig_branch = run_hg(["branch"]).strip()

    is_at_pull_point = False;
    while True:
        svn_info = get_svn_info(".")
        svn_current_rev = svn_info["last_changed_rev"]
        # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted'
        repos_url = svn_info["repos_url"]
        # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted/branches/xmpp-subprotocols-2178-2'
        wc_url = svn_info["url"]
        assert wc_url.startswith(repos_url)
        # e.g. u'/branches/xmpp-subprotocols-2178-2'
        wc_base = wc_url[len(repos_url):]

        svn_branch = wc_url.split("/")[-1]

        svn_branch = check_branchmap(svn_branch, wc_base, options)

        if is_at_pull_point: 
            break
        is_at_pull_point = True;
        
        if options.prefere2hg and not options.tip_rev:
            # Prepare and/or switch named branches
            if orig_branch != svn_branch:
                if hg_is_clean(orig_branch):
                # Update to or create the "pristine" branch
                    svn_base = svn_base_of_branch(orig_branch)
                    (svn_syncrev, hg_syncrev)=get_svn_rev_of_hgbranch(orig_branch)
                    if not (svn_syncrev is None):
                        ui.status("svn follow hg(%s-%s) to %s@%d",orig_branch, hg_syncrev, svn_base, svn_syncrev);
                        svn_switch_to(repos_url+svn_base, svn_syncrev, clean=False, ignore_ancetry=True)
                        continue;
        break

    # Get remote SVN info
    svn_greatest_rev = get_svn_info(wc_url)['last_changed_rev']

    if svn_greatest_rev != svn_current_rev:
        # We can't go on if the pristine branch isn't up to date.
        # If the pristine branch lacks some revisions from SVN we are not
        # able to pull them afterwards.
        # For example, if the last SVN revision in out hgsvn repository is
        # r100 and the latest SVN revision is r101, hgpushsvn would create
        # a tag svn.102 on top of svn.100, but svn.101 isn't in hg history.
        print ("Branch '%s' out of date. Run 'hgpullsvn' first."
               % svn_branch)
        return 1

    # Switch branches if necessary.
    if orig_branch != svn_branch:
        if not hg_switch_branch(orig_branch, svn_branch):
            return 1

    hg_start_rev = "svn.%d" % svn_current_rev
    hg_revs = None
    hg_tree = None
    try:
        hg_start_cset = get_hg_cset(hg_start_rev)
    except RuntimeError:
        if not options.force:
            raise
        hg_start_cset = get_hg_cset("0")
        print "Warning: revision '%s' not found, forcing to first rev '%s'" % (
            hg_start_rev, hg_start_cset)
    else:
        #hg_start_branch = get_branch_from_hg(hg_start_cset)
        if not options.collapse:
            hg_revs,hg_tree = get_hg_revs_with_graph(hg_start_cset, svn_branch, last_rev=options.tip_rev)
            # if branch started, branch head not enlisted in hg_revs, 
            # thus use hg_start_cset as start from wich 1st branch revision borns
            if strip_hg_rev(hg_start_cset) not in hg_revs :
                if IsDebug():
                    print "start rev %s not in push set %s" %(hg_start_cset, hg_revs)
                start_parents = get_parents_from_hg(hg_revs[0])
                if IsDebug():
                    print "start rev parent %s expects at start point %s" %(start_parents, hg_start_cset)
                if ([hg_start_cset] == start_parents) or options.force:
                    # hgbranch starts right from svn_curent, so can commit branch head
                    hg_revs = [strip_hg_rev(hg_start_cset)] + hg_revs;
                else:
                    raise HgSVNError("head of branch <%s> is not in svn yet, have to push ones head-branch first" % svn_branch)
    if hg_revs is None:
        hg_revs = [strip_hg_rev(hg_start_cset), strip_hg_rev(get_hg_cset(options.tip_rev))]


    pushed_svn_revs = []
    allok = True;
    try:
        if options.dryrun:
            print "Outgoing revisions that would be pushed to SVN:"
        try:
            if IsDebug():
                print "processing revisions set:%s" % hg_revs
            for prev_rev, next_rev in get_pairs(hg_revs):
                if not options.dryrun:
                    
                    if not options.edit:
                        ui.status("Committing changes up to revision %s",
                                    get_hg_cset(next_rev))
                    username = options.username
                    if options.keep_author:
                        username = run_hg(["log", "-r", next_rev,
                                            "--template", "{author}"])
                    if is_anonimous_branch_head(prev_rev, hg_tree):
                        ui.status("revision %s is a switch point for multiple anonimous branches"
                                  ", cant distingish wich way to up" % prev_rev)
                        return 2
                    
                    svn_merged = False
                    if hg_tree.has_key(next_rev):
                        if IsDebug():
                            print "target rev %s have parents %s" %(next_rev, hg_tree[next_rev][0])
                        if len(hg_tree[next_rev][0])>1:
                            ui.status("revision %s is a merge point" % next_rev)
                            if (options.merge_branches == "break") or (options.merge_branches == ""):
                                ui.status("break due to merging not enabled", level=ui.DEFAULT)
                                return 4
                            if options.merge_branches == "skip":
                                ui.status("skip branches of merge")
                            else:
                              if hg_sync_merge_svn(prev_rev, next_rev, hg_tree, svn_branch, options=options):
                                svn_merged = True
                                ui.status("ok: revision %s merges fine" % next_rev)
                              else:
                                if options.merge_branches != "trypush":
                                    return 3
                                ui.status("failed to branches of merge, so normal commit")
                            
                    svn_rev = hg_push_svn(prev_rev, next_rev,
                                            edit=options.edit,
                                            username=username,
                                            password=options.password,
                                            cache=options.cache,
                                            options=options
                                            , use_svn_wc = svn_merged
                                            )
                    if svn_rev:
                        # Issue 95 - added update to prevent add/modify/delete crash
                        run_svn(["up", "--ignore-externals"])
                        map_svn_rev_to_hg(svn_rev, next_rev, local=True)
                        pushed_svn_revs.append(svn_rev)
                else:
                    print run_hg(["log", "-r", next_rev,
                              "--template", "{rev}:{node|short} {desc}"])
        except:
            # TODO: Add --no-backup to leave a "clean" repo behind if something
            #   fails?
            run_hg(["revert", "--all"])
            raise

    except:
        allok = False

    if clean and not IsDebug():
        work_branch = orig_branch
        if work_branch != svn_branch:
            run_hg(["up", "-C", work_branch])
            run_hg(["branch", work_branch])

    if not allok:
        return 5

    if pushed_svn_revs:
        if len(pushed_svn_revs) == 1:
            msg = "Pushed one revision to SVN: "
        else:
            msg = "Pushed %d revisions to SVN: " % len(pushed_svn_revs)
        run_svn(["up", "-r", pushed_svn_revs[-1]])
        ui.status("%s %s", msg, ", ".join(str(x) for x in pushed_svn_revs))
        try:
          for line in run_hg(["st"]).splitlines():
            if line.startswith("M"):
                ui.status(("Mercurial repository has local changes after "
                           "SVN update."))
                ui.status(("This may happen with SVN keyword expansions."))
                break
        except:
            ui.status("Cant check repository status")
            
    elif not options.dryrun:
        ui.status("Nothing to do.")

    return 0

def on_option_svnignore_add(option, opt, value, parser):
    if (opt == "--svnignore-use"):
        append_ignore4svn(value)
    elif (opt == "--svnignore-save"):
        save_svnignores()

def main():
    # Defined as entry point. Must be callable without arguments.
    usage = "usage: %prog [-cf]"
    parser = OptionParser(usage)
    parser.add_option("-f", "--force", default=False, action="store_true",
                      dest="force",
                      help="push even if no hg tag found for current SVN rev.")
    parser.add_option("-c", "--collapse", default=False, action="store_true",
                      dest="collapse",
                      help="collapse all hg changesets in a single SVN commit")
    parser.add_option("-r", type="string", dest="tip_rev", default="", 
                        help="limit push up to specified revision")
    parser.add_option("--branch", type="string", dest="svn_branch",
        help="override branch name (defaults to last path component of <SVN URL>)")
    parser.add_option("-n", "--dry-run", default=False, action="store_true",
                      dest="dryrun",
                      help="show outgoing changes to SVN without pushing them")
    parser.add_option("-e", "--edit", default=False, action="store_true",
                      dest="edit",
                      help="edit commit message using external editor")
    parser.add_option("-a", "--noversioned_change", type="string", default="abort",
                      dest="on_noversioned_change",
                      help="=<add> - add to svn repo files that noverioned, <skip> - ignore this changes")
    parser.add_option("--merge-branches", default="break", type="string",
                      dest="merge_branches",
                      help=("<push> - try to push named branches at merge point,"
                            "registered in branches map                         "
                            "\n<skip> - commit as ordinary revision             "
                            "\n<trypush> - if cant push branches, commit as ordinary revision"
                            "\n<>|<break> - default:do not merge, and break pushing"
                           )
                      )
    parser.add_option("-u", "--username", default=None, action="store", type="string",
                      dest="username",
                      help="specify a username ARG as same as svn --username")
    parser.add_option("-p", "--password", default=None, action="store", type="string",
                      dest="password",
                      help="specify a password ARG as same as svn --password")
    parser.add_option("--no-auth-cache", default=False, action="store_true",
                      dest="cache",
                      help="Prevents caching of authentication information")
    parser.add_option("--keep-author", default=False, action="store_true",
                      dest="keep_author",
                      help="keep the author when committing to SVN")
    parser.add_option("--svnignore-use", type="string", action="callback", callback=on_option_svnignore_add,
                      help="ignore hg-versioned file from committing to SVN")
    parser.add_option("--svnignore-save", action="callback", callback=on_option_svnignore_add,
                      help=("save svnignores permanently: - add it to .svnignore list")
                     )
    parser.add_option("--svn-accept", type="string", default="mine-conflict", dest="svnacception",
                      help=("defines avn accept options for merge cmd")
                     )
    load_svnignores()
    load_hgsvn_branches_map()
    (options, args) = run_parser(parser, __doc__)
    if args:
        display_parser_error(parser, "incorrect number of arguments")
    return locked_main(real_main, options, args)

if __name__ == "__main__":
    sys.exit(main() or 0)

