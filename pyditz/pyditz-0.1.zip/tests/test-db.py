"""
Database tests.
"""

import shutil
from filecmp import dircmp
from nose.tools import raises

from ditz.database import DitzDB, DitzError
from ditz.flags import *

desc = """
blah blah blah blah blah blah blah blah blah blah blah blah blah
blah blah blah blah blah blah blah blah blah blah blah blah blah
blah blah blah blah blah blah blah blah blah blah blah blah blah
"""


def test_create(name="database"):
    "Test database creation"

    try:
        shutil.rmtree(name)
    except OSError:
        pass

    db = DitzDB("MyProject", path=name, usecache=True, autosave=True)
    print db

    db.add_component("default")
    db.add_release('0.1')
    db.add_release('0.2')

    issue = db.add_issue("Something to do", desc)
    db.add_reference(issue, "file.txt")

    issue = db.add_issue("Critical fix", desc, comment="Really urgent")

    db.set_release(issue, '0.1')
    db.set_release(issue, '0.2')
    db.set_release(issue, None)

    db.add_comment(issue, "Will you make up your mind?")

    db.set_status(issue, IN_PROGRESS, comment="Let's do it!")
    db.set_status(issue, PAUSED, comment="Er.. let's think about it")
    db.set_status(issue, CLOSED, WONTFIX, comment="Nah, let's not bother")

    for issue in db:
        print issue

    db.write()

    issue = db.add_issue("Another issue")
    db.write()

    db.drop_issue(issue)
    db.write()

    newdb = DitzDB.read(name, usecache=True)
    assert len(newdb.issues) == 2

    newdb = DitzDB.read(name, usecache=False)
    assert len(newdb.issues) == 2


@raises(DitzError)
def test_nosuchcomp():
    "Test nonexistent component"

    db = DitzDB("MyProject")
    db.add_issue("Issue 1", component='fred')


@raises(DitzError)
def test_norelease():
    "Test nonexistent release"

    db = DitzDB("MyProject")
    db.add_component("default")
    db.add_issue("Issue 1", release='1.0')


@raises(DitzError)
def test_duprelease():
    "Test duplicate releases"

    db = DitzDB("MyProject")
    db.add_release("0.2")
    db.add_release("0.2")


@raises(DitzError)
def test_invalidrelease_1():
    "Test invalid release (no issues)"

    db = DitzDB("MyProject")
    db.add_release("0.1")
    db.release_release("0.1")


@raises(DitzError)
def test_invalidrelease_2():
    "Test invalid release (issue not closed)"

    db = DitzDB("MyProject")
    db.add_release("0.1")
    db.add_issue("Issue 1", release='0.1')
    db.release_release("0.1")


@raises(DitzError)
def test_invalidrelease_3():
    "Test invalid release (no such release)"

    db = DitzDB("MyProject")
    db.release_release("0.1")


@raises(DitzError)
def test_invalidrelease_4():
    "Test invalid release (already released)"

    db = DitzDB("MyProject")
    db.add_issue("Issue 1", release='0.1', status=CLOSED)
    db.release_release("0.1")
    db.release_release("0.1")


@raises(DitzError)
def test_dupcomponent():
    "Test duplicate components"

    db = DitzDB("MyProject")
    db.add_component("doc")
    db.add_component("doc")


def test_copy(name="example"):
    "Test database copying and roundtripping"

    db = DitzDB.read(name)
    db.write(name + "-copy")

    def check_files(dcmp):
        for name in dcmp.diff_files:
            raise Exception("file '%s' differs" % name)

        for sub_dcmp in dcmp.subdirs.values():
            check_files(sub_dcmp)

    dcmp = dircmp(name, name + "-copy")
    check_files(dcmp)


def test_convert():
    "Test conversion between names and IDs in strings"

    db = DitzDB("MyProject")
    issue = db.add_issue("A bug")

    text = db.convert_to_id("This is issue ID myproject-1")
    assert text == "This is issue ID {issue %s}" % issue.id

    text = db.convert_to_name("This is issue name {issue %s}" % issue.id)
    assert text == "This is issue name myproject-1"

    name = db.issue_name(issue)
    assert name == "myproject-1"

    otherissue = db.get_issue(name)
    assert otherissue == issue
