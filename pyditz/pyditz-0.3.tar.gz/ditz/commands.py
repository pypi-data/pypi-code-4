"""
Ditz command handler.
"""

import os
import re
import sys

from cmd import Cmd
from database import DitzDB
from objects import find_config
from util import print_columns, error, default_name, default_email, DitzError

from flags import (STATUS, IN_PROGRESS, PAUSED, CLOSED, DISPOSITION,
                   FIXED, WONTFIX, REORG, BUGFIX, FEATURE, TASK,
                   UNRELEASED)


class DitzCmd(Cmd):
    prompt = "Ditz: "

    def __init__(self, path=".", **kwargs):
        Cmd.__init__(self)

        #: Whether running interactively.
        self.interactive = kwargs.pop("interactive", False)

        #: Whether to skip asking for comments.
        self.nocomments = kwargs.pop("nocomment", False)

        #: Comment string to use in non-interactive mode.
        self.comment = kwargs.pop("comment", None)

        #: Database (read when required).
        self._db = None

        #: Arguments for reading database.
        self._dbargs = (os.path.realpath(path), kwargs)

        #: Last issue name mentioned.
        self.last_issuename = None

        #: Last release name mentioned.
        self.last_releasename = None

        #: list of available commands.
        self.commands = set()

        # Set up list of known commands.
        for name in self.get_names():
            if name.startswith("do_"):
                self.commands.add(name[3:])

        # If interactive, set things up right now.
        if self.interactive:
            self.initdb()

    @property
    def db(self):
        self.initdb()
        return self._db

    def initdb(self):
        """
        Read or create the Ditz database, if not already done.
        """

        if not self._db:
            path, kwargs = self._dbargs
            if self.interactive:
                if find_config(path):
                    print "Reading Ditz database in", path
                    print
                else:
                    print "Setting up Ditz database in", path
                    print
                    if not self.setup():
                        sys.exit()

            self._db = DitzDB.read(path, **kwargs)

        return self._db

    def setup(self):
        """
        Set up a database interactively.
        """

        config = self.getconfig()
        if config:
            name, email, issuedir = config
        else:
            return

        path, kwargs = self._dbargs
        project = self.getline("Project name", os.path.basename(path))
        if not project:
            return

        db = DitzDB(project, name, email, issuedir, path, **kwargs)
        db.write()

        print
        print "Ditz database created in", path

        return True

    # Command methods.

    def do_add(self, arg):
        "add -- Add an issue"

        self.initdb()

        title = self.getline("Title: ")
        if not title:
            return

        desc = self.gettext("Description")
        if desc is None:
            return

        types = {'b': BUGFIX, 'f': FEATURE, 't': TASK}

        while True:
            reply = self.getline("Is this a (b)ugfix, (f)eature or (t)ask? ")
            if reply and reply[0] in types:
                issuetype = types[reply[0]]
                break

        release = None
        releases = self.db.project.releases
        choices = [rel.name for rel in releases if rel.status == UNRELEASED]
        if choices and self.getyesno("Assign to a release now?"):
            if len(choices) > 1:
                release = self.getchoice("release", choices)
            else:
                release = choices[0]
                print "Assigning to release", release

            if not release:
                return

        default = self.db.config.username
        prompt = 'Issue creator (enter for "%s"): ' % default
        reporter = self.getline(prompt)
        comment = self.getcomment()
        if comment is None:
            return

        issue = self.db.add_issue(title, desc, type=issuetype,
                                  reporter=reporter, release=release,
                                  comment=comment)

        print "Added issue", self.db.issue_name(issue)
        return True

    def do_add_component(self, arg):
        "add-component [name] -- Add a component"

        self.initdb()

        name = self.getarg(arg, 1) or self.getline("Name: ")
        if not name:
            return

        self.db.add_component(name)
        print "Added component", name
        return True

    def do_add_reference(self, arg):
        "add-reference <issue> -- Add a reference to an issue"

        self.initdb()

        issue = self.getissue(arg, 1)
        if not issue:
            return

        name = self.db.issue_name(issue)
        print "Adding a reference to %s: %s" % (name, issue.title)
        text = self.getline("Reference: ")
        if not text:
            return

        comment = self.getcomment()
        if comment is None:
            return

        self.db.add_reference(issue, text, comment=comment)
        print "Added reference to", name
        return True

    def do_add_release(self, arg):
        "add-release [name] -- Add a release"

        self.initdb()

        name = self.getarg(arg, 1) or self.getline("Name: ")
        if not name:
            return

        print "Adding release", name
        comment = self.getcomment()
        if comment is None:
            return

        self.db.add_release(name, comment=comment)
        print "Added release", name
        return True

    def do_archive(self, arg):
        "archive <release> [dir] -- Archive a release"

        self.initdb()

        name = self.getrelease(arg, 1)
        if not name:
            return

        path = self.getarg(arg, 2)
        if not path:
            path = "ditz-archive-%s" % name

        self.db.archive_release(name, path)
        print "Archived to", path

    def do_assign(self, arg):
        "assign <issue> [release] -- Assign an issue to a release"

        self.initdb()

        issue = self.getissue(arg, 1)
        if not issue:
            return

        name = self.db.issue_name(issue)
        if issue.release:
            print "Issue %s currently assigned to release %s" % \
                  (name, issue.release)
        else:
            print "Issue %s not currently assigned to any release" % name

        release = self.getarg(arg, 2)

        if not release:
            releases = self.db.project.releases
            choices = [rel.name for rel in releases]

            if issue.release:
                choices.remove(issue.release)

            if not choices:
                error("no other release available")
                return

            if len(choices) > 1:
                release = self.getchoice("release", choices)
            else:
                release = choices[0]

        if not release:
            return

        if release == issue.release:
            error("already assigned to release %s" % release)
            return

        if not self.db.get_release(release):
            error("no release with name %s" % release)
            return

        print "Assigning to release", release
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_release(issue, release, comment=comment)
        return True

    def do_changelog(self, arg):
        "changelog <release> -- Generate a changelog for a release"

        self.initdb()

        name = self.getrelease(arg, 1)
        if not name:
            return

        print self.db.show_changelog(name)
        return True

    def do_close(self, arg):
        "close <open_issue> -- Close an issue"

        self.initdb()

        issue = self.getissue(arg, 1)
        if not issue:
            return

        name = self.db.issue_name(issue)
        print "Closing issue %s: %s" % (name, issue.title)

        disp = DISPOSITION
        revdisp = {disp[x]: x for x in disp}
        choices = (disp[FIXED], disp[WONTFIX], disp[REORG])
        choice = self.getchoice("disposition", choices)
        if not choice:
            return

        disp = revdisp[choice]
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_status(issue, CLOSED, disposition=disp, comment=comment)
        print "Closed issue", name, "with disposition", choice
        return True

    def do_comment(self, arg):
        "comment <issue> -- Comment on an issue"

        self.initdb()

        issue = self.getissue(arg, 1)
        if not issue:
            return

        name = self.db.issue_name(issue)
        print "Commenting on %s: %s" % (name, issue.title)

        comment = self.getcomment()

        if comment:
            self.db.add_comment(issue, comment)
            print "Comments recorded for", name
        else:
            print "Empty comment, aborted"

        return True

    def do_drop(self, arg):
        "drop <issue> -- Drop an issue"

        self.initdb()

        issue = self.getissue(arg, 1)
        if not issue:
            return

        name = self.db.issue_name(issue)
        self.db.drop_issue(issue)
        print "Dropped %s.  Other issue names may have changed." % name
        return True

    def do_edit(self, arg):
        "edit <issue> -- Edit an issue"

        self.initdb()
        return self.unimplemented()

    def do_grep(self, arg):
        "grep <string> -- Show issues matching a string or regular expression"

        self.initdb()

        string = self.getarg(arg, 1)
        if not string:
            error("no regexp specified")
            return

        try:
            regexp = re.compile(string)
        except re.error as msg:
            error("invalid regexp: %s" % str(msg))
            return

        print self.db.show_grep(regexp) or "No matching issues"
        return True

    def do_html(self, arg):
        "html [dir] -- Generate HTML status pages"

        self.initdb()
        return self.unimplemented()

    def do_init(self, arg):
        "init -- Initialize the issue database for a new project"

        path = find_config(self._dbargs[0])
        if path:
            dirname = os.path.split(path)[0]
            error("Ditz database already exists in %s" % dirname)
            return

        self.setup()

    def do_log(self, arg):
        "log [count] -- Show recent activity"

        self.initdb()

        count = self.getint(arg, 1)
        for line in self.db.log_events(count=count, verbose=True):
            print line

        return True

    def do_reconfigure(self, arg):
        "reconfigure -- Rerun configuration script"

        db = self.db
        config = self.getconfig(db.config)
        if not config:
            return

        name, email, issuedir = config
        db.config.name = name
        db.config.email = email
        db.config.issue_dir = issuedir

        db.config.write(self.db.path)
        print "Configuration written"

    def do_release(self, arg):
        "release <unreleased_release> -- Release a release"

        self.initdb()

        name = self.getrelease(arg, 1)
        if not name:
            return

        comment = self.getcomment()
        if comment is None:
            return

        self.db.release_release(name, comment)
        print "Released", name
        return True

    def do_releases(self, arg):
        "releases -- Show releases"

        self.initdb()

        print self.db.show_releases() or "No releases"
        return True

    def do_set_component(self, arg):
        "set-component <issue> [component] -- Set an issue's component"

        self.initdb()

        issue = self.getissue(arg, 1)
        comp = self.getarg(arg, 2)
        if not issue:
            return

        name = self.db.issue_name(issue)
        print "Changing the component of issue %s: %s" % (name, issue.title)

        choices = self.db.components
        if len(choices) < 2:
            error("this project does not use multiple components")
            return

        if comp and comp not in choices:
            error("unknown component: %s" % comp)
            return

        if not comp:
            choices.remove(issue.component)
            comp = self.getchoice("component", choices)
            if not comp:
                return

        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_component(issue, comp, comment)
        newname = self.db.issue_name(issue)

        print "Issue %s is now %s.  Other issue names " \
              "may have changed" % (name, newname)

        return True

    def do_shortlog(self, arg):
        "shortlog [count] -- Show recent activity (short form)"

        self.initdb()

        count = self.getint(arg, 1)
        for line in self.db.log_events(count=count):
            print line

        return True

    def do_show(self, arg):
        "show <issue> -- Describe a single issue"

        self.initdb()

        issue = self.getissue(arg, 1)
        if issue:
            print self.db.show_issue(issue)

        return True

    def do_start(self, arg):
        "start <unstarted_issue> -- Start work on an issue"

        self.initdb()

        issue = self.getissue(arg, 1)
        if not issue:
            return

        if issue.status == IN_PROGRESS:
            error("already marked as " + STATUS[issue.status])
            return

        name = self.db.issue_name(issue)
        print "Starting work on %s: %s" % (name, issue.title)
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_status(issue, IN_PROGRESS, comment=comment)
        print "Recorded start of work for", name
        return True

    def do_status(self, arg):
        "status [release] -- Show project status"

        self.initdb()

        release = self.getrelease(arg, 1, optional=True)
        print self.db.show_status(release)

    def do_stop(self, arg):
        "stop <started_issue> -- Stop work on an issue"

        self.initdb()

        issue = self.getissue(arg, 1)
        if not issue:
            return

        if issue.status == PAUSED:
            error("already marked as " + STATUS[issue.status])
            return

        name = self.db.issue_name(issue)
        print "Stopping work on %s: %s" % (name, issue.title)
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_status(issue, PAUSED, comment=comment)
        print "Recorded stopping of work for", name
        return True

    def do_todo(self, arg):
        "todo [-a,all] [release] -- Generate todo list"

        self.initdb()

        flag = self.getarg(arg, 1)
        if flag in ("-a", "all"):
            release = self.getrelease(arg, 2, optional=True)
            closed = True
        else:
            release = self.getrelease(arg, 1, optional=True)
            closed = False

        print self.db.show_todo(release, closed)
        return True

    def do_unassign(self, arg):
        "unassign <assigned_issue> -- Unassign an issue from any releases"

        self.initdb()

        issue = self.getissue(arg, 1)
        if not issue:
            return

        if not issue.release:
            error("not assigned to a release")
            return

        print "Unassigning %s: %s" % (self.db.issue_name(issue), issue.title)
        comment = self.getcomment()
        if comment is None:
            return

        self.db.set_release(issue, None, comment=comment)
        return True

    def do_shell(self, arg):
        "shell -- run a system command"
        os.system(arg)
        return True

    def do_path(self, arg):
        "path -- show the root Ditz database path"

        self.initdb()
        print self.db.path
        return True

    def do_quit(self, arg):
        "quit -- quit the interactive command loop"
        sys.exit()

    do_EOF = do_quit

    # Completion methods.

    def match_issue(self, text, line, beg, end):
        return startswith(self.db.issue_names, text)

    complete_add_reference = match_issue
    complete_assign = match_issue
    complete_close = match_issue
    complete_comment = match_issue
    complete_drop = match_issue
    complete_edit = match_issue
    complete_set_component = match_issue
    complete_show = match_issue
    complete_start = match_issue
    complete_stop = match_issue
    complete_unassign = match_issue

    def match_release(self, text, line, beg, end):
        return startswith(self.db.releases, text)

    complete_archive = match_release
    complete_release = match_release
    complete_status = match_release
    complete_todo = match_release

    def match_command(self, text):
        return startswith(self.commands, text)

    # Command hook methods.

    def onecmd(self, cmd):
        args = cmd.split()

        if args:
            args[0] = args[0].replace('-', '_')

            if args[0] not in self.commands:
                matches = self.match_command(args[0])
                if len(matches) == 1:
                    args[0] = matches[0]
                elif len(matches) > 1:
                    print "Ambiguous command: %s (%s)" % \
                          (args[0], ", ".join(matches))
                    return False

        try:
            retval = Cmd.onecmd(self, " ".join(args))
        except DitzError as msg:
            error(msg)
            retval = False

        return None if self.interactive else retval

    def emptyline(self):
        return self.onecmd("todo")

    def default(self, arg):
        if self.interactive:
            print "Unknown command:", arg, "(type 'help' for a list)"
        else:
            error("unknown command: %s" % arg)

        return False

    # Input methods.

    def getarg(self, arg, idx):
        """
        Get a string argument.
        """

        args = arg.split()
        return args[idx - 1] if len(args) >= idx else None

    def getint(self, arg, idx, default=None):
        """
        Get an integer.
        """

        value = self.getarg(arg, idx)
        if not value:
            return default

        try:
            return int(value)
        except ValueError:
            error("expected an integer, not", value)
            return default

    def getissue(self, arg, idx):
        """
        Get an issue by name.
        """

        name = self.getarg(arg, idx)
        if not name and self.last_issuename:
            name = self.last_issuename

        if not name:
            error("no issue specified")
            return None

        self.last_issuename = name
        issue = self.db.get_issue(name)
        if not issue:
            error("no issue with name '%s'" % name)
            return None

        return issue

    def getrelease(self, arg, idx, optional=False):
        """
        Get a release by name.
        """

        name = self.getarg(arg, idx)
        if not name and optional:
            return None

        if not name and self.last_releasename:
            name = self.last_releasename

        if not name:
            error("no release specified")
            return None

        self.last_releasename = name
        if name not in self.db.releases:
            error("no release with name '%s'" % name)
            return None

        return name

    def getline(self, prompt="> ", default="", interrupt=True):
        """
        Get a single line of input.
        """

        if default:
            prompt = "%s (default: %s): " % (prompt, default)

        # This is a bit naughty, and copies some internals of the Cmd
        # module.  But if the function had been exposed in the first place,
        # I wouldn't have to, would I?
        if self.use_rawinput:
            try:
                return raw_input(prompt) or default
            except EOFError:
                return None
            except KeyboardInterrupt:
                if interrupt:
                    print
                    return None
                else:
                    raise
        else:
            self.stdout.write(prompt)
            self.stdout.flush()
            line = self.stdin.readline()
            if not len(line):
                return default
            else:
                return line.rstrip('\r\n')

    def gettext(self, title=None, prompt="> ", endchar='.'):
        """
        Get multiline text.
        """

        if title:
            print title + " (ctrl-c to abort, %s to finish)" % endchar

        try:
            lines = []
            while True:
                line = self.getline(prompt, interrupt=False)
                if not line or line == endchar:
                    return "\n".join(lines)

                lines.append(line)
        except KeyboardInterrupt:
            print
            print "Aborted"
            return None

    def getchoice(self, thing, choices):
        """
        Get a choice of several things.
        """

        items = []
        for num, entry in enumerate(choices, 1):
            item = "%3d) %s" % (num, entry)
            items.append(item)

        print_columns(items)
        prompt = "Choose a %s (1--%d): " % (thing, len(choices))

        while True:
            reply = self.getline(prompt)
            if not reply:
                return None

            try:
                return choices[int(reply) - 1]
            except (ValueError, IndexError):
                pass

    def getcomment(self):
        """
        Get a comment string.
        """

        if self.nocomments:
            return ""
        elif not self.interactive and self.comment:
            return self.comment
        else:
            return self.gettext("Comments")

    def getyesno(self, question, default=False):
        """
        Get the answer to a yes/no question.
        """

        prompt = question + " [%s] " % ("yes" if default else "no")

        while True:
            reply = self.getline(prompt)
            if not reply:
                return default
            if reply[0] in "yY":
                return True
            elif reply[0] in "nN":
                return False

    def getconfig(self, oldconfig=None):
        """
        Prompt for and return database configuration info.
        """

        default = oldconfig.name if oldconfig else default_name()
        name = self.getline("Your name", default)
        if not name:
            return

        default = oldconfig.email if oldconfig else default_email()
        email = self.getline("Your email", default_email())
        if not email:
            return

        default = oldconfig.issue_dir if oldconfig else "issues"
        issuedir = self.getline("Issue directory", default)
        if not issuedir:
            return

        return name, email, issuedir

    # Miscellaneous other stuff.

    def unimplemented(self):
        cmd = self.lastcmd.split()[0]
        print "Sorry, '%s' is not implemented yet" % cmd
        return False


def startswith(items, text):
    return filter(lambda x: x.startswith(text), items)
