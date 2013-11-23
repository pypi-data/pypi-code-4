"""
Ditz database interface.
"""

import os
import re
import glob
import cPickle as pickle

from collections import Counter
from datetime import datetime

from objects import Config, Project, Issue, Component, Release, find_config

from util import (read_yaml_file, age, extract_username, default_name,
                  default_email, DitzError)

from flags import (RELEASED, UNRELEASED, BUGFIX, FEATURE, TASK, UNSTARTED,
                   STATUS, DISPOSITION, TYPE, TYPE_PLURAL, CLOSED, FLAGS)


class DitzDB(object):
    def __init__(self, project, username=None, email=None,
                 issuedir=None, path=".", autosave=False,
                 usecache=False, cachefile=".ditz-cache",
                 verbose=False):
        #: Configuration data.
        self.config = Config(username or default_name(),
                             email or default_email(),
                             issuedir or ".ditz-issues")

        #: Location.
        self.path = os.path.realpath(path)

        #: Project data.
        self.project = Project(project)

        #: List of issues.
        self.issues = []

        #: Whether to save files when changes are made.
        self.autosave = autosave

        #: Whether to use issue cache.
        self.usecache = usecache

        #: Issue cache filename.
        self.cachefile = cachefile

        #: Whether to be verbose.
        self.verbose = verbose

        #: Mapping of issue IDs to assigned names.
        self._id2name = {}

        #: Mapping of assigned names to issues.
        self._name2issue = {}

    # High-level database commands.

    def add_issue(self, title, desc="", type=BUGFIX, status=UNSTARTED,
                  disposition=None, creation_time=None, reporter=None,
                  component=None, release=None, comment=None):
        """
        Add a new issue.
        """

        issue = Issue(title, desc, type, status, disposition, creation_time,
                      reporter or self.config.username)

        self.set_component(issue, component, event=False)
        self.set_release(issue, release, event=False)

        self.issues.append(issue)
        self.add_event(issue, "created", comment)
        self.update_issue_names()

        self.save(issue)
        return issue

    def add_component(self, name):
        """
        Add a new component.
        """

        comp = Component(name)

        if name not in self.components:
            self.project.components.append(comp)
        else:
            raise DitzError("component already exists: %s" % name)

        self.save()
        return comp

    def add_release(self, name, status=UNRELEASED, release_time=None,
                    comment=None):
        """
        Add a new release.
        """

        if not self.get_release(name):
            rel = Release(name, status, release_time)
            self.add_event(rel, "created", comment)
            self.project.releases.append(rel)
        else:
            raise DitzError("release already exists: %s" % name)

        self.save()
        return rel

    def add_reference(self, issue, reference, comment=None):
        """
        Add a reference to an issue.
        """

        num = issue.add_reference(reference)
        self.add_event(issue, "added reference %d" % num, comment)
        self.save(issue)

    def set_status(self, issue, status, disposition=None, comment=None):
        """
        Set the status of an issue.
        """

        prevstatus = issue.status

        issue.set_status(status)
        issue.set_disposition(disposition)

        if disposition:
            text = "closed with disposition %s" % DISPOSITION[disposition]
        else:
            text = "changed status from %s to %s" % \
                   (STATUS[prevstatus], STATUS[status])

        self.add_event(issue, text, comment)
        self.save(issue)

    def set_component(self, issue, component=None, comment=None, event=True):
        """
        Set the component of an issue.
        """

        if not component:
            component = self.project.name
        elif component not in self.components:
            raise DitzError("unknown component: %s" % component)

        if event:
            text = "assigned to component %s from %s" \
                   % (component, issue.component)
            self.add_event(issue, text, comment)

        issue.component = component
        self.update_issue_names()
        self.save(issue)

    def set_release(self, issue, release=None, comment=None, event=True):
        """
        Set the release of an issue.
        """

        if release and not self.get_release(release):
            raise DitzError("unknown release: %s" % release)

        if issue.release == release:
            return

        if event:
            if release:
                text = "assigned to release " + release
                if issue.release:
                    text += " from release " + issue.release
                else:
                    text += " from unassigned"
            else:
                text = "unassigned from release %s" % issue.release

            self.add_event(issue, text, comment)

        issue.release = release
        self.save(issue)

    def release_release(self, name, comment=None):
        """
        Release a release.
        """

        rel = self.get_release(name)
        if not rel:
            raise DitzError("unknown release: %s" % name)

        if rel.status == RELEASED:
            raise DitzError("release '%s' is already released" % name)

        count = 0
        for issue in self.issues:
            if issue.release == name:
                count += 1
                if issue.status != CLOSED:
                    raise DitzError("open issue %s must be reassigned"
                                    % self.issue_name(issue))

        if count == 0:
            raise DitzError("no issues assigned to release '%s'" % name)

        rel.status = RELEASED
        rel.release_time = datetime.now()

        self.add_event(rel, "released", comment)
        self.save()

    def archive_release(self, name, path):
        """
        Archive a release.
        """

        rel = self.get_release(name)
        if not rel:
            raise DitzError("unknown release: %s" % name)

        if rel.status != RELEASED:
            raise DitzError("release '%s' has not been released" % name)

        keep = []
        archive = []
        for issue in self.issues:
            if issue.release == name:
                archive.append(issue)
            else:
                keep.append(issue)

        if not archive:
            raise DitzError("no issues assigned to release %s" % name)

        try:
            os.makedirs(path)
        except OSError as msg:
            raise DitzError("can't create %s: %s" % (path, str(msg)))

        self.project.write(path)
        for issue in archive:
            issue.write(path)

        for issue in archive:
            path = self.issue_filename(issue)
            if os.path.exists(path):
                os.remove(path)

        self.issues = keep
        self.update_issue_names()

        self.save()

    def drop_issue(self, issue):
        """
        Drop an issue.
        """

        path = self.issue_filename(issue)
        if os.path.exists(path):
            os.remove(path)

        self.issues.remove(issue)
        self.update_issue_names()

        self.save()

    def add_comment(self, issue, comment):
        """
        Add a comment to an issue.
        """

        self.add_event(issue, "commented", comment)
        self.save(issue)

    def show_grep(self, regexp):
        """
        Return text describing issues that match a regexp.
        """

        issues = [issue for issue in self.issues if issue.grep(regexp)]

        if issues:
            return "\n".join(self.list_issues(issues))
        else:
            return None

    def show_todo(self, release=None, closed=False):
        """
        Return text describing unresolved issues.
        """

        if not release:
            releases = [r for r in self.project.releases
                        if r.status == UNRELEASED] + [None]
        else:
            releases = [r for r in self.project.releases
                        if r.name == release]

        lines = []
        add = lines.append

        for num, rel in enumerate(releases):
            if num > 0:
                add('')

            if rel:
                text = rel.name
                if rel.status == UNRELEASED:
                    text += " (unreleased)"
                add(text + ":")
            else:
                add("Unassigned:")

            show = []
            for issue in self.issues:
                if rel and issue.release != rel.name:
                    continue
                elif not rel and issue.release:
                    continue
                elif not closed and issue.status == CLOSED:
                    continue

                show.append(issue)

            if not show:
                add("No issues" if closed else "No open issues")
                continue

            for text in self.list_issues(sorted(show, reverse=True)):
                add(text)

        return "\n".join(lines)

    def show_issue(self, issue, attrfmt="%11s: %s", underline='-'):
        """
        Return text describing an issue.
        """

        lines = []
        add = lines.append
        addattr = lambda attr, val="": add(attrfmt % (attr, val))

        title = "Issue %s" % self.issue_name(issue)
        add(title)
        add(underline * len(title))

        addattr("Title", issue.title)

        desc = self.convert_to_name(issue.desc)

        if "\n" in desc:
            addattr("Description")
            for line in desc.split("\n"):
                add("  " + line)
        else:
            addattr("Description", issue.desc)

        add('')
        addattr("Type", TYPE[issue.type])

        if issue.status == CLOSED:
            addattr("Status", "closed: " + DISPOSITION[issue.disposition])

        addattr("Creator", issue.reporter)
        addattr("Age", age(issue.creation_time))
        addattr("Release", issue.release or "")

        addattr("References")
        for num, ref in enumerate(issue.references, 1):
            add("%3d. %s" % (num, ref))

        addattr("Identifier", issue.id)

        add('')
        add("Event log:")

        for date, email, text, comment in reversed(issue.log_events):
            add("- %s (%s, %s ago)" % (text, extract_username(email),
                                       age(date)))
            if comment:
                for line in self.convert_to_name(comment).split("\n"):
                    add('  > ' + line)

        return "\n".join(lines)

    def show_releases(self):
        """
        Return text describing all releases.
        """

        lines = []
        add = lines.append

        for rel in reversed(self.project.releases):
            if rel.status == UNRELEASED:
                tag = "unreleased"
            else:
                tag = "released %s" % (rel.release_time.strftime("%Y-%m-%d"))

            add("%s (%s)" % (rel.name, tag))

        return "\n".join(lines)

    def show_changelog(self, name):
        """
        Return text describing a changelog for a release.
        """

        rel = self.get_release(name)
        if not rel:
            raise DitzError("unknown release: %s" % name)

        lines = []
        add = lines.append

        text = "== " + rel.name + " / "
        if rel.status == RELEASED:
            text += rel.release_time.strftime("%Y-%m-%d")
        else:
            text += "unreleased"

        add(text)

        for issue in sorted(self.issues, key=lambda x: x.type):
            if issue.release == rel.name:
                if issue.status != CLOSED:
                    continue

                if issue.type == BUGFIX:
                    text = "bugfix: " + issue.title
                else:
                    text = issue.title

                add("* " + text)

        return "\n".join(lines)

    def show_status(self, release=None, maxflags=20):
        """
        Return text describing the status of a release or releases.
        """

        if not release:
            releases = [r for r in self.project.releases
                        if r.status == UNRELEASED] + [None]
        else:
            releases = [r for r in self.project.releases
                        if r.name == release]

        data = []
        for rel in releases:
            reldata = []
            data.append(reldata)
            reldata.append(rel.name if rel else "unassigned")

            issues = []
            alltotal = allclosed = 0
            for itype in BUGFIX, FEATURE, TASK:
                closed = total = 0

                for issue in self.issues:
                    if issue.type != itype:
                        continue
                    elif rel and issue.release != rel.name:
                        continue
                    elif not rel and issue.release:
                        continue

                    total += 1
                    if issue.status == CLOSED:
                        closed += 1

                    issues.append(issue)

                alltotal += total
                allclosed += closed

                text = "%2d/%2d %s" % (closed, total, TYPE_PLURAL[itype])
                reldata.append(text)

            if not rel:
                text = ""
            elif rel.status == RELEASED:
                text = "(released)"
            elif alltotal == 0:
                text = "(no issues)"
            elif allclosed == alltotal:
                text = "(ready for release)"
            else:
                flags = map(lambda x: FLAGS[x.status], sorted(issues))
                if len(flags) > maxflags:
                    newflags = []

                    for i in xrange(maxflags):
                        factor = float(i) / (maxflags - 1)
                        idx = int(factor * (len(flags) - 1))
                        newflags.append(flags[idx])

                    flags = newflags

                text = "".join(flags)

            reldata.append(text)

        maxlen = [0] * 5
        for reldata in data:
            for col in xrange(5):
                maxlen[col] = max(maxlen[col], len(reldata[col]))

        lines = []
        for reldata in data:
            for col in xrange(5):
                if col in (0, 4):
                    reldata[col] = reldata[col].ljust(maxlen[col])
                else:
                    reldata[col] = reldata[col].rjust(maxlen[col])

            lines.append("  ".join(reldata))

        return "\n".join(lines)

    def log_events(self, verbose=False, count=None, datefmt="%a %b %d %X %Y"):
        """
        Yield log event messages.
        """

        events = sorted(self.issue_events, key=lambda x: x[0], reverse=True)
        for num, (date, email, text, comment, issue) in enumerate(events):
            if count and num >= count:
                break

            name = self.issue_name(issue)
            when = age(date)

            if verbose:
                lines = []
                add = lines.append

                add('date   : %s (%s ago)' % (date.strftime(datefmt), when))
                add('author : %s' % email)
                add('issue  : [%s] %s' % (name, issue.title))
                add('')
                add('  ' + text)

                if comment:
                    for line in self.convert_to_name(comment).split("\n"):
                        add('  > ' + line)

                add('')

                yield "\n".join(lines)
            else:
                user = extract_username(email)
                yield "%10s | %10s | %15s | %s" % (when, name, user, text)

    # Low-level commands and properties.

    def add_event(self, item, text, comment=None):
        """
        Add an event to a database item.
        """

        item.event(self.config.username, text, comment)

    def get_issue(self, name):
        """
        Return an issue given its assigned issue name.
        """

        return self._name2issue.get(name, None)

    def issue_name(self, issue):
        """
        Return the assigned issue name of an issue.
        """

        return self._id2name.get(issue.id, "<invalid-issue>")

    def issue_filename(self, issue):
        """
        Return the filename of an issue.
        """

        return os.path.join(self.path, self.config.issue_dir, issue.filename)

    def get_release(self, name):
        """
        Return a release given its name.
        """

        name = str(name)
        for rel in self.project.releases:
            if rel.name == name:
                return rel

        return None

    def list_issues(self, issues):
        """
        Return text description lines for a list of issues.
        """

        lines = []
        maxlen = max(len(self.issue_name(issue)) for issue in issues)

        for issue in issues:
            text = FLAGS[issue.status] + " "
            text += self.issue_name(issue).rjust(maxlen)
            text += ": " + issue.title

            if issue.type == BUGFIX:
                text += " (bug)"
            elif issue.type == FEATURE:
                text += " (feature)"

            lines.append(text)

        return lines

    @property
    def issue_names(self):
        """
        All existing issue names.
        """

        return sorted(self._name2issue.keys())

    @property
    def issue_events(self):
        """
        Yield all issue-related events and their issues.
        """

        for issue in self.issues:
            for date, user, text, comment in issue.log_events:
                yield date, user, text, comment, issue

    @property
    def components(self):
        """
        List of defined components.
        """

        return [comp.name for comp in self.project.components]

    @property
    def releases(self):
        """
        List of defined releases.
        """

        return [rel.name for rel in self.project.releases]

    # Database input/output methods.

    @staticmethod
    def read(dirname, **kwargs):
        """
        Read a Ditz database.
        """

        # Create an empty database.
        db = DitzDB("empty", **kwargs)

        # Find the Ditz config file.
        path = find_config(dirname, error=True)
        dirname = os.path.split(path)[0]

        # Read it.
        db.message("reading config from %s" % path)
        config = read_yaml_file(path)

        # Extract the issue directory name.
        try:
            issuedir = config.issue_dir
        except AttributeError:
            raise DitzError("'%s' does not define 'issue_dir'" % path)

        # Read the project file.
        path = os.path.join(dirname, issuedir, Project.filename)
        db.message("reading project from %s" % path)
        project = read_yaml_file(path)

        # Read the issues.
        issues = []
        match = os.path.join(dirname, issuedir, Issue.template % "*")
        issue_files = set(glob.glob(match))

        path = os.path.join(dirname, db.cachefile)
        cached_issues = db.readcache(path)
        cache_changed = False

        if cached_issues:
            # Check for new, modified or deleted issues.
            cached_files = set()
            modtime = os.stat(path).st_mtime

            for issue in cached_issues:
                path = os.path.join(dirname, issuedir, issue.filename)

                # Skip issue if it's deleted.
                if not os.path.exists(path):
                    continue

                # Reread issue file if newer than cache.
                if os.stat(path).st_mtime > modtime:
                    db.message("reading changed issue from %s" % path)
                    issue = read_yaml_file(path)
                    cache_changed = True

                cached_files.add(path)
                issues.append(issue)

            # Read all the new issues.
            for path in issue_files - cached_files:
                db.message("reading new issue from %s" % path)
                issue = read_yaml_file(path)
                issues.append(issue)
                cache_changed = True
        else:
            db.message("reading issues from %s" % issuedir)
            for path in issue_files:
                issue = read_yaml_file(path)
                issues.append(issue)
                cache_changed = True

        # Initialise database.
        db.path = os.path.realpath(dirname)
        db.config = config
        db.project = project
        db.issues = issues

        if cache_changed:
            db.update_cache()

        db.update_issue_names()

        return db

    def readcache(self, path):
        """
        Read cached issues if possible.
        """

        if not self.usecache or not os.path.exists(path):
            return None

        self.message("reading issue cache from %s" % path)

        with open(path) as fp:
            try:
                issues = pickle.load(fp)
            except Exception as msg:
                self.message("removing issue cache (%s)" % str(msg))
                os.unlink(path)
                issues = None

        return issues

    def write(self, dirname=None):
        """
        Write the database.
        """

        if not dirname:
            dirname = self.path
        else:
            self.path = dirname

        # Write the config file.
        self.config.write(dirname)

        # Write the project file.
        path = os.path.join(dirname, self.config.issue_dir)
        self.project.write(path)

        # Write the issues.
        for issue in self.issues:
            issue.write(path)

        # Update issue cache.
        self.update_cache()

    def save(self, issue=None):
        """
        Save database file if required.
        """

        if not self.autosave:
            return

        if issue:
            self.message("saving issue %s" % self.issue_name(issue))
            issue.write(self.issuedir)
            self.update_cache()
        else:
            self.message("saving project")
            self.project.write(self.issuedir)

    def update_cache(self):
        """
        Update the issue cache.
        """

        if self.usecache:
            path = os.path.join(self.path, self.cachefile)
            self.message("writing issue cache to %s" % path)
            with open(path, "w") as fp:
                pickle.dump(self.issues, fp)

    # Issue name/ID handling methods.

    def convert_to_id(self, text):
        """
        Replace names with {issue ...} in text.
        """

        def repl(m):
            issue = self._name2issue.get(m.group(1), None)

            if issue:
                return "{issue %s}" % issue.id
            else:
                return m.group(0)

        return re.sub(r'\b([A-Za-z]+-[0-9]+)\b', repl, text)

    def convert_to_name(self, text, idmap={}):
        """
        Replace {issue ...} with names in text.
        """

        def repl(m):
            idx = m.group(1)
            if idx in idmap:
                return idmap[idx]
            else:
                return self._id2name[idx]

        return re.sub(r'{issue ([0-9a-f]+)}', repl, text)

    def update_issue_names(self):
        """
        Reassign issue names after changes to issue status.
        """

        self.message("updating issue names")
        self.issues.sort()
        counts = Counter()

        self._id2name = {}
        self._name2issue = {}

        for issue in sorted(self.issues, key=lambda x: x.creation_time):
            comp = issue.component.lower()
            counts[comp] += 1
            name = "%s-%d" % (comp, counts[comp])
            self._id2name[issue.id] = name
            self._name2issue[name] = issue

    # Miscellaneous other stuff.

    def message(self, msg):
        """
        Print a message if being verbose.
        """

        if self.verbose:
            print "# " + msg

    @property
    def issuedir(self):
        return os.path.join(self.path, self.config.issue_dir)

    def __iter__(self):
        return iter(self.issues)

    def __repr__(self):
        return "<DitzDB: %s>" % self.path
