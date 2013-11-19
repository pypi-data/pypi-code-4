#!/usr/bin/env python

"""
Unit tests for the veracity.objects module.
"""

import unittest
from unittest.mock import patch, Mock

import os
import shutil
import tempfile
import logging

from veracity import vv
from veracity.vv import VeracityException
from veracity.vscript import VeracityScriptException
from veracity.objects import identify, keywords
from veracity.objects import Repository, WorkingCopy, Item
from veracity.objects import Changeset, Branch, Tag, Stamp, User
from veracity.objects import BuildRequest

from veracity.test import TEST_REPO, REASON
from veracity.test import log, create_temp_repo, delete_temp_repo


def setUpModule():  # pylint: disable=C0103
    """Create a temporary repository for this module's tests.
    """
    global TEMP_REPO  # pylint: disable=W0601
    TEMP_REPO = create_temp_repo(__name__)


def tearDownModule():  # pylint: disable=C0103
    """Delete the temporary repository.
    """
    delete_temp_repo(__name__, TEMP_REPO)


class TestRepository(unittest.TestCase):  # pylint: disable=R0904
    """Unit tests on the Repository class."""  # pylint: disable=C0103

    pass


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestRepositoryIntegration(unittest.TestCase):
    """Integration tests on the Repository class."""  # pylint: disable=C0103

    def test_init_existing(self):
        """Verify a repository can be created from an existing repository."""
        repo = Repository(TEST_REPO.name)
        log(repo)
        self.assertEqual(TEST_REPO, repo)
        self.assertEqual(TEST_REPO.name, repo)
        self.assertNotEqual("", repo)
        self.assertNotEqual(None, repo)

    def test_init_clone(self):
        """Verify a repository can be created as a clone."""
        with Repository(TEMP_REPO.name + '-clone', remote=TEMP_REPO) as repo:
            log(repo)

            repo._push_time = 0  # force push, pylint: disable=W0212
            repo.add_tag('_temptag2', branch=Branch.MASTER)  # tag will get pushed to TEMP_REPO
            self.assertIn('_temptag2', TEMP_REPO.tags)

            TEMP_REPO.add_tag('_temptag', branch=Branch.MASTER)
            repo._pull_time = 0  # force push, pylint: disable=W0212
            self.assertIn('_temptag', repo.tags)  # tag will get pulled  from TEMP_REPO
            self.assertIn('_temptag', TEMP_REPO.tags)

    def test_init_new(self):
        """Verify a new repository can be created."""
        with Repository(TEMP_REPO.name + '-new', create=True) as repo:
            log(repo)
            self.assertEqual(TEMP_REPO.name + '-new', str(repo))

    def test_init_new_no_create(self):
        """Verify an exception occurs when creation of new repositories is disabled."""
        self.assertRaises(VeracityException, Repository, TEMP_REPO.name + '-new', create=False)

    def test_delete(self):
        """Verify a repository can not be used after it is deleted."""
        repo2 = Repository(TEMP_REPO.name + '-clone', remote=TEMP_REPO.name)
        with Repository(TEMP_REPO.name + '-clone', remote=TEMP_REPO.name) as repo:
            log(repo, repo2)
            self.assertEqual(repo, repo2)
        self.assertRaises(VeracityException, repo.delete)
        repo2.delete()  # already deleted

    def test_getattr(self):
        """Verify attribute access behaves normally for repositories."""
        self.assertRaises(AttributeError, getattr, TEST_REPO, '_invalid')

    def test_pull_push_with_no_remote(self):
        """Verify a non-cloned repository can handle pull/push."""
        TEST_REPO.pull()
        TEST_REPO.push()

    def test_exception_in_context_manager(self):
        """Verify an exception in handled in a repository context manager."""
        def will_raise():
            """Raise an exception in a repository context manager."""
            with Repository(TEMP_REPO.name + '-new', create=True) as repo:
                log(repo)
                raise Exception("test exception")
        self.assertRaises(Exception, will_raise)

    def test_export(self):
        self.assertRaises(NotImplementedError, TEMP_REPO.export, None)

    def test_zip(self):
        self.assertRaises(NotImplementedError, TEMP_REPO.zip, None)


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestWorkingCopy(unittest.TestCase):
    """Integration tests on the WorkingCopy class."""  # pylint: disable=C0103

    def test_init_instance(self):
        """Verify a working copy can be checked out from an existing Repository instance."""
        with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
            log(wc)
            self.assertTrue(os.path.isdir(wc.path))
            self.assertFalse(wc.status())

    def test_init_existing(self):
        """Verify a working copy can be checked out from an existing repository."""
        with WorkingCopy(tempfile.mkdtemp(), repo=TEST_REPO.name) as wc:
            log(wc)
            self.assertTrue(os.path.isdir(wc.path))
            self.assertEqual(wc.path, str(wc))

    def test_init_path(self):
        """Verify a working copy can be creating from an existing path."""
        temp = tempfile.mkdtemp()
        with WorkingCopy(temp, repo=TEST_REPO.name) as wc1:
            with WorkingCopy(wc1.path) as wc2:
                log(wc1, wc2)
                self.assertEqual(wc1, wc2)
                self.assertNotEqual(temp, wc1)  # types are different

    def test_init_new(self):
        """Verify a working copy can be checked out to a new path."""
        temp = tempfile.mkdtemp()
        shutil.rmtree(temp)  # force the checkout to create this directory
        with WorkingCopy(temp, repo=TEST_REPO.name) as wc:
            log(wc)
            self.assertEqual(temp, wc.path)

    def test_init_path_invalid(self):
        """Verify a working copy cannot be created from an invalid path."""
        self.assertRaises(VeracityException, WorkingCopy, "not/a/path")

    def test_delete(self):
        """Verify a working copy can not be used after it is deleted."""
        with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
            log(wc)
            self.assertTrue(wc.valid())
        self.assertFalse(wc.valid())
        self.assertRaises(VeracityException, wc.delete)

    def test_getattr(self):
        """Verify attribute access behaves normally for working copies."""
        with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
            self.assertRaises(AttributeError, getattr, wc, '_invalid')

    def test_update(self):
        """Verify a working copy can be updated to a branch and revision."""
        with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
            cs1 = wc.update(branch='master')
            self.assertEqual('master', wc.branch)
            cs2 = wc.update(rev=1)
            self.assertNotEqual('master', wc.branch)
            self.assertNotEqual(cs1.rev, cs2.rev)

    def test_chdir(self):
        """Verify a working copy sub-directory can be entered."""
        with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
            log(wc)
            os.mkdir(os.path.join(wc.path, 'temp'))
            wc.chdir('temp')
            self.assertTrue(wc.status())

    def test_copy(self):
        """Verify a working copy can be copied."""
        with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
            log(wc)
            with wc.copy(wc.path + '-copy') as wc2:
                self.assertNotEqual(wc, wc2)
                self.assertEqual(wc.repo, wc2.repo)
                self.assertTrue(os.path.isdir(wc2.path))

    def test_exception_in_context_manager(self):
        """Verify an exception in handled in a working copy context manager."""
        def will_raise():
            """Raise an exception in a repository context manager."""
            with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
                log(wc)
                raise Exception("test exception")
        self.assertRaises(Exception, will_raise)

    def test_commit(self):
        with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
            log(wc)
            self.assertRaises(NotImplementedError, wc.commit, None)

    def test_merge(self):
        with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
            log(wc)
            self.assertRaises(NotImplementedError, wc.merge)

    def test_resolve(self):
        with TEST_REPO.checkout(tempfile.mkdtemp()) as wc:
            log(wc)
            self.assertRaises(NotImplementedError, wc.resolve)


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestChangeset(unittest.TestCase):
    """Integration tests on the Changeset class."""  # pylint: disable=C0103

    DICTIONARY = {'revision': ['1:abc123'],
                  'branch': ['master'],
                  'tag': ['123', '456']}

    def test_repo_history(self):
        """Verify the history list can be retrieved from a repository."""
        self.assertLessEqual(3, len(TEST_REPO.history))

    def test_repo_heads(self):
        """Verify the heads list can be retrieved from a repository."""
        heads = TEST_REPO.heads
        self.assertLessEqual(1, len(heads))
        self.assertLessEqual(1, len(heads[0].branches))

    def test_branches(self):
        """Verify the branches list can be retrieved from a changeset."""
        cs = Changeset(self.DICTIONARY)
        log(cs)
        self.assertEqual(1, len(cs.branches))
        self.assertIn('master', cs.branches)

    def test_tags(self):
        """Verify the tags list can be retrieved from a changeset."""
        cs = Changeset(self.DICTIONARY)
        log(cs)
        self.assertEqual(2, len(cs.tags))
        self.assertIn('123', cs.tags)

    def test_checkout(self):
        """Verify a changeset can be checked out."""
        cs = TEST_REPO.heads[0]
        with cs.checkout(tempfile.mkdtemp()) as wc:
            self.assertTrue(os.path.exists(wc.path))
            self.assertEqual(cs.rev, wc.parent.rev)

    def test_eq(self):
        """Verify changests can be compared."""
        cs1 = Changeset('abc123', repo=TEST_REPO)
        cs2 = Changeset('abc123', repo=TEST_REPO.name)
        cs3 = Changeset('abc123', repo=None)
        cs4 = Changeset('def456', repo=TEST_REPO)
        log(cs1, cs2, cs3, cs4)
        self.assertEqual(cs1, cs1)
        self.assertNotEqual(cs1, cs3)
        self.assertNotEqual(cs1, cs4)
        self.assertEqual('abc123', cs1)
        self.assertNotEqual(None, cs1)

    def test_incoming(self):
        self.assertRaises(NotImplementedError, TEMP_REPO.get_incoming)

    def test_outgoing(self):
        self.assertRaises(NotImplementedError, TEMP_REPO.get_outgoing)

    def test_leaves(self):
        self.assertRaises(NotImplementedError, TEMP_REPO.get_leaves)


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestBranch(unittest.TestCase):
    """Integration tests on the Branch class."""  # pylint: disable=C0103

    def test_repo_branches(self):
        """Verify the branches list can be retrieved from a repo."""
        branches = TEMP_REPO.branches
        log(branches)
        self.assertIn('master', branches)

    def test_repo_add_move_branch(self):
        """Verify a branch can be added and moved."""
        b = TEMP_REPO.add_branch('_temp_branch', branch='master')
        try:
            self.assertEqual('master', b.branch)
            b = b.move(rev=1)
            self.assertEqual(1, b.rev)
        except:
            logging.error("exception will be raised after cleanup...")
            raise
        finally:
            b.remove()

    def test_repo_close_open_branch(self):
        """Verify a branch can be closed and opened"""
        b = Branch('master', repo=TEMP_REPO, branch='master')
        b.close()
        try:
            b.close()  # already closed
            self.assertNotIn(b, TEMP_REPO.branches)
            b.reopen()
        except:
            logging.error("exception will be raised after cleanup...")
            raise
        finally:
            b.reopen()  # already reopened

    def test_eq(self):
        """Verify branches can be compared."""
        b1 = Branch('a', repo=TEMP_REPO, rev=1)
        b2 = Branch('b', repo=TEMP_REPO, rev=1)
        b3 = Branch('b', repo=None, rev=1)
        b4 = Branch('b', repo=None, rev=1)
        log(b1, b2, b3, b4)
        self.assertNotEqual(b2, b3)
        self.assertNotEqual(b1, b2)
        self.assertEqual(b3, b4)
        self.assertNotEqual(None, b1)

    def test_wc_branch(self):
        """Verify the branch can be set on a working copy."""
        with TEMP_REPO.checkout(tempfile.mkdtemp()) as wc:
            wc.branch = '_new_branch'
            self.assertEqual('_new_branch', wc.branch)
            branch = wc.attach('master')
            self.assertEqual('master', branch)

    def test_wc_branch_none(self):
        """Verify setting the working copy's branch to None detaches it."""
        with TEMP_REPO.checkout(tempfile.mkdtemp()) as wc:
            wc.branch = None
            self.assertEqual(None, wc.branch)


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestItem(unittest.TestCase):
    """Integration tests on the Item class."""  # pylint: disable=C0103

    @classmethod
    def setUpClass(cls):
        if TEST_REPO:
            cls.wc = WorkingCopy(tempfile.mkdtemp(), repo=TEMP_REPO)

    @classmethod
    def tearDownClass(cls):
        if TEST_REPO:
            cls.wc.delete()

    def test_init_existing_ws_instance(self):
        """Verify an item can be created from an existing WorkingCopy instance."""
        item = Item("test_file", [], work=self.wc)
        self.assertEqual("test_file", str(item))
        self.assertNotEqual(None, item)

    def test_init_existing_ws_path(self):
        """Verify an item can be created from an existing WorkingCopy path."""
        item = Item("test_file", [], work=self.wc.path)
        self.assertEqual("test_file", str(item))
        self.assertNotEqual(Item("test_file", []), item)
        self.assertNotEqual(Item("test_file", [], work=None), item)

    def test_wc_items_no_changes(self):
        """Verify the items list can be retrieved with no changes."""
        self.wc.revert()
        self.assertEqual([], self.wc.status())

    def test_wc_items_with_changes(self):
        """Verify the items list can be retrieved when there are changes."""
        # Revert all changes
        self.wc.revert()
        # Make changes
        os.chdir(self.wc.path)
        log(os.listdir(self.wc.path))
        with open("foo.h", 'a') as modified:
            modified.write("\n# TEST MODIFICATION")
        with open("NEW.txt", 'w') as found:
            found.write("# FOUND FILE")
        os.remove('bar.c')  # lost
        vv.run('rename', "foo.h", "renamed_foo.h")  # renamed
        # Get items
        items = self.wc.status()
        self.assertEqual(3, len(items))
        self.assertIn(Item("renamed_foo.h", [Item.MODIFIED, Item.RENAMED], work=self.wc), items)
        self.assertIn(Item("NEW.txt", [Item.FOUND], work=self.wc), items)
        self.assertIn(Item("bar.c", [Item.LOST], work=self.wc), items)

    def test_wc_revert(self):
        """Verify a change can be reverted in a working copy."""
        # Revert all changes
        self.wc.revert()
        # Make change
        os.chdir(self.wc.path)
        with open("foo.h", 'a') as modified:
            modified.write("\n# TEST MODIFICATION")
        # Get items
        item = Item("foo.h", [Item.MODIFIED], work=self.wc)
        log(item)
        self.assertIn(item, self.wc.status())
        self.assertNotIn(item.path, self.wc.status())  # wrong type
        # Revert change
        self.wc.revert(item.path)
        # Verify change is gone
        self.assertNotIn(item, self.wc.status())

    def test_lock_unlock(self):
        """Verify a file can be locked and unlocked."""
        self.wc.attach(Branch.MASTER)
        item = Item("bar.c", [], work=self.wc)
        log(item)
        item.lock()
        item.unlock()

    def test_locks(self):
        self.assertRaises(NotImplementedError, TEMP_REPO.get_locks)


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestTag(unittest.TestCase):
    """Integration tests on the Tag class."""  # pylint: disable=C0103

    def test_init(self):
        """Verify a tag can be created."""
        tag = Tag('abc', repo=TEMP_REPO, rev='123')
        self.assertEqual('abc', tag)
        self.assertNotEqual(None, tag)
        self.assertNotEqual(tag, None)

    def test_repo_tags(self):
        """Verify a tag can be added and removed from a repo."""
        try:
            TEMP_REPO.add_tag('_temptag2', branch=Branch.MASTER)
            tag = TEMP_REPO.add_tag('_temptag2', branch=Branch.MASTER)  # returns already created tag
            log(tag)
            self.assertIn(tag, TEMP_REPO.tags)
            self.assertIn('_temptag2', TEMP_REPO.tags)
        except:
            logging.error("exception will be raised after cleanup...")
            raise
        finally:
            TEMP_REPO.remove_tag('_temptag2')
            tag.remove()  # already removed

    def test_repo_move_tag(self):
        """Verify a tag can be moved in a repository."""
        tag = TEMP_REPO.add_tag('_temptag', rev=2)
        log(tag)
        tag = tag.move(rev=1)
        self.assertEqual(1, tag.rev)
        tag.remove()

    def test_no_changset(self):
        """Verify a revision, tag, or branch is required to add a tag."""
        self.assertRaises(ValueError, TEMP_REPO.add_tag, '_invalid')


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestStamp(unittest.TestCase):
    """Integration tests on the Stamp class."""  # pylint: disable=C0103

    def test_init(self):
        """Verify a stamp can be created."""
        stamp = Stamp('abc', repo=TEMP_REPO, rev='123')
        self.assertEqual('abc', stamp)
        self.assertNotEqual(None, stamp)
        self.assertNotEqual(stamp, None)

    def test_repo_stamps(self):
        """Verify a stamp can be added and removed from a repo."""
        TEMP_REPO.add_stamp('_tempstamp', branch=Branch.MASTER)
        stamp = TEMP_REPO.add_stamp('_tempstamp', branch=Branch.MASTER)  # returns already created stamp
        log(stamp)
        self.assertIn(stamp, TEMP_REPO.stamps)
        self.assertIn('_tempstamp', TEMP_REPO.stamps)
        stamp.remove()

    def test_no_changset(self):
        """Verify a revision, tag, or branch is required to add a stamp."""
        self.assertRaises(ValueError, TEMP_REPO.add_stamp, '_invalid')


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestUser(unittest.TestCase):
    """Integration tests on the Tag class."""  # pylint: disable=C0103

    def test_init(self):
        """Verify a user can be created."""
        user = User('_tempuser', repo=TEMP_REPO)
        log(user)
        self.assertEqual('_tempuser', user)
        self.assertNotEqual(User('_tempuser2', repo=TEMP_REPO), user)
        self.assertNotEqual(None, user)

    def test_repo_users(self):
        """Verify the users list can be retrieved from a repository."""
        log(TEMP_REPO.users)
        self.assertIn('_tempuser', TEMP_REPO.users)

    def test_repo_add_user_nobody(self):
        """Verify the 'nobody' user cannot be created."""
        self.assertRaises(VeracityException, TEMP_REPO.add_user, User.NOBODY)

    def test_repo_add_user_existing(self):
        """Verify attempting to add an existing user is handled."""
        user = TEMP_REPO.add_user('testuser')  # default user
        self.assertEqual('testuser', user)

    def test_repo_set_user(self):
        """Verify the current user can be set in a repository."""
        TEMP_REPO.user = '_tempuser'
        self.assertEqual('_tempuser', TEMP_REPO.user)

    def test_repo_rename_user(self):
        """Verify a user can be renamed."""
        u = User('testuser', repo=TEMP_REPO)
        u.set()
        u = u.rename('testuser2')
        try:
            self.assertEqual('testuser2', TEMP_REPO.user)
        except:
            logging.error("exception will be raised after cleanup...")
            raise
        finally:
            u.rename('testuser')

    def test_repo_activate_user(self):
        """Verify a user can be deactivated and activated."""
        u = User('testuser', repo=TEMP_REPO)
        u.deactivate()
        u.deactivate()  # redundant
        u.activate()
        u.activate()  # redundant

    @patch('veracity.vv.run', Mock(side_effect=VeracityException))
    def test_user_empty(self):
        """Verify None is returned when no user is set."""
        self.assertIs(None, TEMP_REPO.user)


@unittest.skipUnless(TEST_REPO, REASON)  # pylint: disable=R0904
class TestBuildRequest(unittest.TestCase):
    """Integration tests on the BuildRequest class."""  # pylint: disable=C0103

    def test_init(self):
        """Verify a build request can be created."""
        request = BuildRequest('abc123', 'def456')
        log(request)
        self.assertEqual('abc123', request)
        self.assertNotEqual(None, request)
        self.assertNotEqual(request, None)
        self.assertEqual(BuildRequest('abc123', None), request)

    def test_repo_request_build(self):
        """Verify a build can be requested in a repository."""
        del TEMP_REPO.builds
        cs = TEMP_REPO.get_heads(branch='master')[0]
        request1 = TEMP_REPO.request_build('test build', 'C', 'W', 'Q', cs.rev, branch='master')
        log(request1)
        self.assertEqual(BuildRequest(request1.bid, None, repo=TEMP_REPO), request1)
        request2 = TEMP_REPO.get_build('W', 'Q')
        log(request2)
        self.assertEqual(request1, request2)

    def test_repo_request_builds(self):
        """Verify multiple builds can be requested in a repository."""
        del TEMP_REPO.builds
        cs = TEMP_REPO.get_heads(branch='master')[0]
        TEMP_REPO.request_build('test build', 'C', 'W', 'Q', cs.rev)
        TEMP_REPO.request_build('test build 2', 'N', 'L', 'Q', cs.rev, branch='master')
        self.assertEqual(2, len(list(TEMP_REPO.get_builds(limit=None))))

    def test_repo_request_build_invalid(self):
        """Verify an exception is raised when requesting an invalid build."""
        self.assertRaises(VeracityScriptException, TEMP_REPO.request_build, '_', 'W', 'W', 'Q', 'fake')

    def test_repo_get_build_no_config(self):
        """Verify None is return when getting builds of an invalid environment."""
        self.assertRaises(VeracityScriptException, TEMP_REPO.get_build, 'W', 'INVALID')

    def test_repo_get_build_no_env(self):
        """Verify None is return when getting builds of an invalid environment."""
        self.assertIsNone(TEMP_REPO.get_build('INVALID', 'Q'))

    def test_repo_get_build_none(self):
        """Verify nothing is returned when no builds are queued."""
        del TEMP_REPO.builds
        self.assertEqual(None, TEMP_REPO.get_build('M', 'Q'))

    def test_update(self):
        """Verify a build request can be updated."""
        cs = TEMP_REPO.get_heads(branch='master')[0]
        request = TEMP_REPO.request_build('testbuild3', 'M', 'M', 'Q', cs.rev)
        log(request)
        self.assertEqual('Q', request.status)
        request.update('B')
        self.assertEqual('B', request.status)
        self.assertRaises(VeracityScriptException, request.update, 'INVALID')

    def test_delete(self):
        """Verify a build request can be deleted."""
        cs = TEMP_REPO.get_heads(branch='master')[0]
        request = TEMP_REPO.request_build('testbuild4', 'C', 'L', 'Q', cs.rev)
        log(request)
        request.delete()
        self.assertEqual(None, request.status)
        self.assertRaises(VeracityScriptException, request.update, 'B')


class TestFunctions(unittest.TestCase):
    """Tests on the module functions."""  # pylint: disable=C0103

    def test_identify_pass(self):
        """Verify a valid identifier is accepted."""
        self.assertEqual((None, '1.0', None), identify(rev=None, tag='1.0', branch=None))

    def test_identify_none(self):
        """Verify a default branch is selected."""
        self.assertEqual((None, None, 'master'), identify(rev=None, tag=None, branch=None, default=True))

    def test_identify_invalid(self):
        """Verify an exception occurs on an invalid identifier."""
        self.assertRaises(ValueError, identify, rev=1, tag=None, branch='master')

    def test_identify_none_no_default(self):
        """Verify an exception occurs when no default is allowed."""
        self.assertRaises(ValueError, identify, rev=None, tag=None, branch=None, default=False)

    def test_keywords(self):
        """Verify keywords are converted to strings."""
        self.assertEqual({'a': 123, 'b': True}, keywords(a=123, b=True, c=False, d=None))


if __name__ == '__main__':
    unittest.main()
