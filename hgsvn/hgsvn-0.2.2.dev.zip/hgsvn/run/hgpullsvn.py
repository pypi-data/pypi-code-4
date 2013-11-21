"""hgpullsvn must be run in a repository created by hgimportsvn. It pulls
new revisions one by one from the SVN repository and converts them into local
Mercurial changesets.

"""

from hgsvn import ui
from hgsvn.common import (
    run_hg, run_svn,
    hg_commit_from_svn_log_entry, hg_exclude_options,
    get_svn_rev_from_hg, hg_switch_branch, hg_is_clean,
    check_for_applied_patches,
    once_or_more, check_branchmap
    , load_hgsvn_branches_map
    , get_hg_cset, strip_hg_rev
    , tag_of_svn, get_hg_cset_of_svn
    , hg_tag_svn_rev, hg_rev_tag_by_svn
    , svn_branch_of_path
    , svn_base_of_branch
    , is_hg_have_branch
    , hg_force_switch_branch
    , get_svn_rev_of_hgbranch
    , hg_subrepos
    , in_pathes
)
from hgsvn.svnclient import (
    get_svn_info, get_svn_versioned_files, iter_svn_log_entries,
    get_svn_client_version, get_svn_status
    , svn_switch_to
    , get_first_svn_log_entry
)
from hgsvn.errors import (
    ExternalCommandFailed, OverwrittenSVNBranch, UnsupportedSVNAction,
)
from hgsvn.run.common import run_parser, display_parser_error
from hgsvn.run.common import locked_main

import sys
import os
import time
import traceback
from optparse import OptionParser
import copy
import re

"""
NOTE: interesting tests:
    * http://svn.python.org/projects/python/trunk/Mac :
        - files with space characters in them just before 45000
        - file and dir renames/removes between 46701 and 46723
"""

repos_url = ""
hgsubrepos = list()

# TODO: an option to enable/disable svn:externals (disabled by default?)

def IsDebug():
    return (ui._level >= ui.DEBUG)


def detect_overwritten_svn_branch(wc_url, svn_rev):
    """
    Detect whether the current SVN branch was in a different location at
    the given revision. This means the current branch was later overwritten
    by another one.
    """
    remote_url = get_svn_info(wc_url, svn_rev)['url']
    if remote_url != wc_url:
        msg = ("The current branch (%s) has been\noverwritten with contents from %s.\n"
            + "hgsvn is unable to fetch history of the original branch.\n"
            + "Also, you will have to do a separate 'hgsvnimport' to pull recent history.\n"
            ) % (wc_url, remote_url)
        raise OverwrittenSVNBranch(msg)

def hg_merge_2wc(rev_number):
    if rev_number is None:
        return
    args = ["merge","-f","--tool","internal:local","-r", rev_number]
    return run_hg(args)

def hg_resolve_all():
    args = ["resolve","--all"]
    return run_hg(args)

def autostart_branch(svn_branch, hg_branch, target_revno, options):
    #take svn_branch origin and ensures it pull in hg, and mark it with branch-head tag
    # branch-head - is starting rev which is copy of original
    global repos_url

    svn_switch_to(repos_url+svn_branch)
    origin = get_first_svn_log_entry('.', 0, target_revno)
    svnrev = origin['revision']
    hgrevid = None
    try:
        hgrevid = get_hg_cset_of_svn(svnrev)
        if (len(hgrevid) == 0):
            raise
        return svnrev
    except:
        # there is no svnbranch origin in hg, check ones source
        paths = origin['changed_paths']
        if len(paths) == 0:
            ui.status("cant determine branch %s origin source"%svn_branch)
            return -1
        path = paths[0]
        source = path['copyfrom_revision']
        if source:
            # now get origin`s source hg-rev, and mark it with origin svntag
            ui.status("branch svn:%s sourced from rev%s"%(svn_branch, source), level = ui.VERBOSE)
            srcid = None
            try:
                srcid = get_hg_cset_of_svn(source)
                if (len(srcid) == 0):
                    raise
            except:
                #there is no source in hg pulled, so try to pull it
                if not pull_branch(get_last_svn_log_entry("." , source, source), options):
                    return -2
                try:
                    srcid = get_hg_cset_of_svn(source)
                except:
                    ui.status("svn:%s still not pulled"%source)
                    return -3
            hg_rev_tag_by_svn(strip_hg_rev(srcid), svnrev);
            return svnrev

    ui.status("cant determine branch svn:%s source"%(svn_branch))
    return -4

def pull_branch(log_entry, options):
        global repos_url

        svn_rev = log_entry['revision'];
        paths = log_entry['changed_paths']
        if len(paths) == 0:
            ui.status("strange svn rev: - with no changes")
            return False
        headpath = paths[0]['path']
        svn_branch, hg_branch = svn_branch_of_path(headpath)
        if svn_branch is None:
            ui.status("cant mutch path %s for branch"%(headpath), level = ui.VERBOSE)
            return False
        ui.status("mutched for branch svn:%s hg:%s"%(svn_branch, hg_branch), level = ui.VERBOSE)

        localops = copy.deepcopy(options)
        localops.svn_rev = svn_rev
        if is_hg_have_branch(hg_branch):
            svn_origin, hg_origin = get_svn_rev_of_hgbranch(hg_branch)
            if svn_origin is None:
                ui.status("hg alredy have branch %s not synched with svn"%hg_branch);
                return False
        else:
            # actualy hg have no such branch so start it from stoponcopy origin
            svn_origin = autostart_branch(svn_branch, hg_branch, svn_rev, localops)
            hg_origin = get_hg_cset_of_svn(svn_origin)

        ok = False
        if svn_origin > 0:
            svn_switch_to(repos_url+'/'+svn_branch, rev_number=svn_origin, clean=True)
            hg_force_switch_branch( hg_branch, strip_hg_rev(hg_origin) )
            localops.force = True
            ok = (real_main(localops, {}) == 0)

        del localops
        return ok

def svn_sync_merge_hg(log_entry, current_rev, svn_wc, wc_url, wc_base, hg_branch, options):
    #   check all parents for branch name, and try to push one branches if can
    #   after all branches complete, merge svn work copy and resolves it for hg_push_svn
    
    # ... and restore .svn directories, if we lost some of them due to removes
    #run_svn(['revert', '--recursive', '.'])
    uiMERGE = ui.DEFAULT
    
    svn_rev = log_entry['revision']
    merge_revs = log_entry['merges']
    merge_parent = merge_revs[0]
    merge_hgrevid = None
    try:
        merge_hgrevid = get_hg_cset_of_svn(merge_parent.revno)
        ui.status("merge for parents: svn:%s hg:%s"%(merge_parent.revno, merge_hgrevid), level=uiMERGE)
    except:
        pass

    if (merge_hgrevid is None) or (len(merge_hgrevid) == 0):
        ui.status("have no pulled parent svn:%s"%merge_parent.revno, level = uiMERGE)
        #try to match parent path with branches list
        if pull_branch(merge_parent.entry, options):
            #switch back to current branch for merging here
            svn_switch_to(wc_url, rev_number=current_rev, clean=True)
            if not hg_force_switch_branch(hg_branch, tag_of_svn(current_rev)):
                raise
        else:
            return False
        merge_hgrevid = get_hg_cset_of_svn(merge_parent.revno)
        ui.status("merge for parents: svn:%s hg:%s"%(merge_parent.revno, merge_hgrevid), level = uiMERGE)

    hg_merge_2wc( strip_hg_rev(merge_hgrevid) )
    hg_resolve_all()
    # and pull like normal svn up
    run_svn(['revert', '--recursive', '.'])

    return True

def pull_svn_rev(log_entry, current_rev, svn_wc, wc_url, wc_base, options):
    """
    Pull SVN changes from the given log entry.
    Returns the new SVN revision. If an exception occurs, it will rollback
    to revision 'current_rev'.
    """
    global hgsubrepos
    
    retry = options.svnretry
    svn_rev = log_entry['revision']

    added_paths = []
    copied_paths = []
    removed_paths = []
    changed_paths = []
    unrelated_paths = []
    replaced_paths = {}

    # 1. Prepare for the `svn up` changes that are pulled in the second step
    #    by analyzing log_entry for the changeset
    for d in log_entry['changed_paths']:
        # e.g. u'/branches/xmpp-subprotocols-2178-2/twisted/words/test/test_jabberxmlstream.py'
        p = d['path']
        if not p.startswith(wc_base + "/"):
            # Ignore changed files that are not part of this subdir
            if p != wc_base:
                unrelated_paths.append(p)
            continue
        
        action = d['action']
        if action not in 'MARD':
            raise UnsupportedSVNAction("In SVN rev. %d: action '%s' not supported. Please report a bug!"
                % (svn_rev, action))
        # e.g. u'twisted/words/test/test_jabberxmlstream.py'
        p = p[len(wc_base):].strip("/")

        if options.subrepo == "skip":
            tmpp = os.path.normcase(os.path.normpath(p))
            if in_pathes(tmpp, hgsubrepos):
                ui.status("skip action on path %s of nested repo" % (p))
                unrelated_paths.append(p)
                continue

        # Record for commit
        changed_paths.append(p)
        if IsDebug():
            ui.status("action %s on path %s" % (action, p))
        # Detect special cases
        old_p = d['copyfrom_path']
        if old_p and old_p.startswith(wc_base + "/"):
            old_p = old_p[len(wc_base):].strip("/")
            if IsDebug():
                ui.status("    is copyed %s" % (old_p))
            # Both paths can be identical if copied from an old rev.
            # We treat like it a normal change.
            if old_p != p:
                # Try to hint hg about file and dir copies
                if not os.path.isdir(old_p):
                    copied_paths.append((old_p, p))
                    if action == 'R':
                        removed_paths.append(old_p)
                else:
                    # Extract actual copied files (hg doesn't track dirs
                    # and will refuse "hg copy -A" with dirs)
                    r = run_hg(["st", "-nc"], [old_p], output_is_locale_encoding=True)
                    for old_f in r.splitlines():
                        f = p + old_f[len(old_p):]
                        copied_paths.append((old_f, f))
                        if action == 'R':
                            removed_paths.append(old_f)
                continue
        if d['action'] == 'A':
            added_paths.append(p)
        elif d['action'] == 'D':
            # Same as above: unfold directories into their affected files
            if not os.path.isdir(p):
                removed_paths.append(p)
            else:
                r = run_hg(["st", "-nc"], [p], output_is_locale_encoding=True)
                for f in r.splitlines():
                    removed_paths.append(f)
        elif d['action'] == 'R':
            # (R)eplaced directories can have added and removed files without
            # them being mentioned in the SVN log => we must detect those files
            # ourselves.
            # (http://svn.python.org/projects/python/branches/py3k, rev 59625)
            if os.path.isdir(p):
                replaced_paths[p] = get_svn_versioned_files(
                    os.path.join(svn_wc, p))
            else:
                # We never know what twisty semantics (R) can have. addremove
                # is safest.
                added_paths.append(p)

    # 2. Update SVN + add/remove/commit hg
    try:
      try:
        if changed_paths:
            args = ["up", "--ignore-externals"]
            if get_svn_client_version() >= (1, 5):
                args.extend(['--accept', 'working'])
            ui.status('Attempting to update to revision %s...', str(svn_rev))
            once_or_more("SVN update", retry, run_svn, args + ["-r", svn_rev, svn_wc])
            conflicts = []
            for status_entry in get_svn_status('.'):
                if status_entry['status'] == 'conflicted':
                    conflicts.append(status_entry['path'])
            if conflicts:
                ui.status('SVN updated resulted in conflicts!', level=ui.ERROR)
                ui.status('Conflicted files: %s', ','.join(conflicts))
                ui.status('Please report a bug.')
                svn_revert_all()

            for p, old_contents in replaced_paths.items():
                old_contents = set(old_contents)
                new_contents = set(get_svn_versioned_files(
                    os.path.join(svn_wc, p)))
                added_paths.extend(p + '/' + f for f in new_contents - old_contents)
                removed_paths.extend(p + '/' + f for f in old_contents - new_contents)
            if added_paths:
                # Use 'addremove' because an added SVN directory may
                # overwrite a previous directory with the same name.
                # XXX what about untracked files in those directories?
                run_hg(["addremove"] + hg_exclude_options, added_paths)
            for old, new in copied_paths:
                try:
                    if not os.path.islink(new) or os.path.exists(new):
                        run_hg(["copy", "-A"], [old, new])
                    else:
                        run_hg(["copy"], [old, new])
                except ExternalCommandFailed:
                    # Maybe the "old" path is obsolete, i.e. it comes from an
                    # old SVN revision and was later removed.
                    s = run_hg(['st', '-nd'], [old], output_is_locale_encoding=True)
                    if s.strip():
                        # The old path is known by hg, something else happened.
                        raise
                    run_hg(["add"], [new])
            if removed_paths:
                for file_path in removed_paths:
                    try:
                        run_hg(["remove", "-A"], [file_path])
                    except (ExternalCommandFailed), e:
                        if str(e).find("file is untracked") > 0:
                            ui.status("Ignoring warnings about untracked files: '%s'" % str(e), level=ui.VERBOSE)
                        else:
                            raise
            hg_commit_from_svn_log_entry(log_entry)
        elif unrelated_paths:
            detect_overwritten_svn_branch(wc_url, svn_rev)
      except (ExternalCommandFailed), e:
        if str(e).find("inside nested repo") > 0:
            if options.subrepo != "skip":
                raise
            ui.status("\n try skip of nested repo affects", level=ui.VERBOSE)
            nestpath = re.search(r"path '(?P<npath>\S+)'", str(e))
            nestrepo = re.search("repo '(?P<nrepo>\S+)'", str(e))
            if nestpath is None:
                ui.status("uncknown abort of nested repo output format");
                raise
            npath = nestpath.group("npath")
            nrepo = nestrepo.group("nrepo")
            nrepo = os.path.normcase(os.path.normpath(nrepo))
            if nrepo in hgsubrepos:
                ui.status("\n try path:%s of nested repo:%s alredy skip, and it not help" % (npath, nrepo))
                raise
            ui.status("\n try skip path:%s of nested repo:%s" % (npath, nrepo), level=ui.VERBOSE)
            hgsubrepos.append(nrepo)
            return pull_svn_rev(log_entry, current_rev, svn_wc, wc_url, wc_base, options)
        else:
            raise

    # NOTE: in Python 2.5, KeyboardInterrupt isn't a subclass of Exception anymore
    except (Exception, KeyboardInterrupt), e:
        ui.status("\nInterrupted, please wait for cleanup!\n", level=ui.ERROR)
        state = run_hg(["status", "-v"])
        ui.status("hg:\n"+state, level=ui.ERROR);
        # NOTE: at this point, running SVN sometimes gives "write lock failures"
        # which leave the WC in a weird state.
        time.sleep(0.3)
        run_svn(["cleanup"])
        raise
        hgsvn_rev = get_svn_rev_from_hg()
        if hgsvn_rev != svn_rev:
            # Unless the tag is there, revert to the last stable state
            run_svn(["up", "--ignore-externals", "-r", current_rev, svn_wc])
            run_hg(["revert", "--all"])
        raise

    return svn_rev

def real_main(options, args):
    global repos_url

    if check_for_applied_patches():
        print ("There are applied mq patches. Put them aside before "
               "running hgpullsvn.")
        return 1
    svn_wc = "."
    orig_branch = run_hg(["branch"]).strip()

    is_at_pull_point = False;
    while True:
        # Get SVN info
        svn_info = get_svn_info('.')
        current_rev = svn_info['revision']
        next_rev = current_rev + 1
        # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted'
        repos_url = svn_info['repos_url']
        # e.g. u'svn://svn.twistedmatrix.com/svn/Twisted/branches/xmpp-subprotocols-2178-2'
        wc_url = svn_info['url']
        assert wc_url.startswith(repos_url)
        # e.g. u'/branches/xmpp-subprotocols-2178-2'
        wc_base = wc_url[len(repos_url):]
        # e.g. 'xmpp-subprotocols-2178-2'
        svn_branch = wc_url.split("/")[-1]
        svn_branch = check_branchmap(svn_branch, wc_base, options)
        
        if is_at_pull_point: 
            break
        is_at_pull_point = True;
        
        if options.prefere2hg and not options.svn_peg:
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
    
    if options.svn_peg:
       wc_url += "@" + str(options.svn_peg)
    
    # Get remote SVN info
    ui.status("Retrieving remote SVN info...", level=ui.VERBOSE)
    svn_greatest_rev = get_svn_info(wc_url)['last_changed_rev']

    synched_svnrev = None
    synched_hgrev  = None
    if options.prefere2hg and not options.svn_peg:
        #try to go to latest synched revision
        if orig_branch == svn_branch:
            if hg_is_clean(orig_branch):
                (synched_svnrev, synched_hgrev)=get_svn_rev_of_hgbranch(orig_branch)
                if not (synched_svnrev is None):
                    next_rev = synched_svnrev+1

    if svn_greatest_rev < next_rev:
        ui.status("No revisions after %s in SVN repo, nothing to do",
                  svn_greatest_rev)
        return
    elif options.svn_rev != None:
        if options.svn_rev < next_rev:
            ui.status("All revisions up to %s are already pulled in, "
                      "nothing to do",
                      options.svn_rev)
            return
        svn_greatest_rev = options.svn_rev

    # Show incoming changes if in dry-run mode.
    if options.dryrun:
        ui.status("Incoming SVN revisions:")
        for entry in iter_svn_log_entries(wc_url, next_rev, svn_greatest_rev,
                                          options.svnretry):
            if entry["message"]:
                msg = entry["message"].splitlines()[0].strip()
            else:
                msg = ""
            line = "[%d] %s (%s)" % (entry["revision"], msg, entry["author"])
            ui.status(line)
        return

    # Prepare and/or switch named branches
    if orig_branch != svn_branch:
        # Update to or create the "pristine" branch
        synched_svnrev = None
        if not hg_switch_branch(orig_branch, svn_branch):
            return 1
    elif not hg_is_clean(svn_branch):
        return 1

    # Detect that a previously aborted hgpullsvn retrieved an SVN revision
    # without committing it to hg.
    # If there is no SVN tag in current head, we may have been interrupted
    # during the previous "hg tag".

    #if options.force:
    hgsvn_rev = None
    if (synched_svnrev is None) and (not options.svn_peg):
            #since not defined peg revision, try find last synch rev
            try:
                synched_svnrev, synched_hgrev = get_svn_rev_of_hgbranch(svn_branch)
            except:
                hgsvn_rev = get_svn_rev_from_hg()
                synched_svnrev = None

    if synched_svnrev is not None and synched_svnrev != current_rev:
        ui.status(("\nNote: hgsvn repository is in an unclean state "
                   "(probably because of an aborted hgpullsvn). \n"
                   "Let's first update to the last good SVN rev:%s."%synched_svnrev),
                  level=ui.VERBOSE)
        run_svn(["revert", "-R", "."])
        run_svn(["up", "--ignore-externals", "-r", synched_svnrev, svn_wc])
        current_rev = synched_svnrev
        next_rev = synched_svnrev + 1

    # Reset working branch to last svn head to have a clean and linear SVN
    # history.
    heads_before = None
    if hgsvn_rev is None:
        heads_before = run_hg(["heads", "--template",
                               "{node}%s" % os.linesep]).splitlines()
        run_hg(["update", "-C", "svn.%d" % current_rev])

    # Load SVN log starting from current rev
    it_log_entries = iter_svn_log_entries(wc_url, next_rev, svn_greatest_rev, options.svnretry)

    try:
        try:
            for log_entry in it_log_entries:
                merged = False
                if not (log_entry['merges'] is None):
                    # merges are for merge point
                    if options.merge_branches == "break":
                        ui.status("Pulled r%d is a merge of revs:%s"
                                , log_entry["revision"]
                                , log_entry['merges']
                                )
                        return 2
                    elif (options.merge_branches == "pull") or (options.merge_branches == "trypull"):
                        if svn_sync_merge_hg(
                                log_entry
                                , current_rev, svn_wc, wc_url, wc_base, svn_branch
                                , options) :
                            merged = True
                        else:
                            if options.merge_branches != "trypull":
                                return 3
                            ui.status("failed to branches of merge, so normal commit")
                    #elif options.merge_branches == "skip":

                current_rev = pull_svn_rev(log_entry, current_rev,
                                           svn_wc, wc_url, wc_base, options)
                if current_rev is None:
                    return 1
                ui.status("Pulled r%d %s (%s)", log_entry["revision"],
                          log_entry["message"], log_entry["author"])

        # TODO: detect externals with "svn status" and update them as well

        finally:
            if heads_before is not None:  # we have reset the SVN branch
                heads_now = run_hg(["heads", "--template",
                                    "{node}%s" % os.linesep]).splitlines()
                if len(heads_now) != len(heads_before):
                    ui.status("created new head in branch '%s'", svn_branch)
            work_branch = orig_branch or svn_branch
            if work_branch != svn_branch:
                run_hg(["up", '-C', work_branch])
                run_hg(["branch", work_branch])
        return 0

    except KeyboardInterrupt:
        ui.status("\nStopped by user.", level=ui.ERROR)
    except ExternalCommandFailed, e:
        ui.status(str(e), level=ui.ERROR)
    except:
        ui.status("\nCommand failed with following error:\n", level=ui.ERROR)
        traceback.print_exc()


def main():
    global subrepos

    # Defined as entry point. Must be callable without arguments.
    usage = "usage: %prog [-p SVN_PEG] [--help]"
    parser = OptionParser(usage)
    parser.add_option("-r", type="int", dest="svn_rev",
       help="limit pull up to specified revision")
    parser.add_option("-p", "--svn-peg", type="int", dest="svn_peg",
       help="SVN peg revision to locate checkout URL")
    parser.add_option("-n", "--dry-run", dest="dryrun", default=False,
                      action="store_true",
                      help="show incoming changesets without pulling them")
    parser.add_option("-f", "--force", default=False, action="store_true",
                      dest="force",
                      help=" forces go to last pulled rev and proceeds from there"
                      )
    parser.add_option("--branch", type="string", dest="svn_branch",
        help="override branch name (defaults to last path component of <SVN URL>)")
    parser.add_option("--svn-retry", dest="svnretry", default=False,
                      action="store_true",
                      help="retry SVN update command on failure")
    parser.add_option("-s", "--subrepo", dest="subrepo", type="string", default="break",
                      help="- defines operation on subrepo affected files"
                           "\n[<break>] - stops pulling if subrepo affected"
                           "\n<skip> - skips subrepo files from operations"
                     )
    parser.add_option("--merge-branches", default="break", type="string",
                      dest="merge_branches",
                      help=("\n<pull> - pull all parent braches                 "
                            "\n<trypull> - same, but forced to commit even if   "
                            "\n         parents cant be pulled fine             "
                            "\n<skip> - commit as ordinary revision             "
                            "\n<>|<break> - default:do not merge, and break pushing"
                           )
                      )
    load_hgsvn_branches_map()
    hgsubrepos = hg_subrepos();
    (options, args) = run_parser(parser, __doc__)
    if args:
        display_parser_error(parser, "incorrect number of arguments")
    return locked_main(real_main, options, args)


if __name__ == "__main__":
    sys.exit(main() or 0)
