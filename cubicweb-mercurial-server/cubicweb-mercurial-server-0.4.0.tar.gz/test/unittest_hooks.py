# -*- coding: utf-8 -*-
import os.path as osp

from mercurial import commands, hg, ui

from cubicweb import Unauthorized, ValidationError, Binary
from cubicweb.devtools.testlib import CubicWebTC

from cubes.mercurial_server.utils import mscui
from cubes.mercurial_server.testutils import MercurialServerTCMixin

class HooksBasicTC(MercurialServerTCMixin, CubicWebTC):
    # msc = MercurialServerConfig

    def test_nonascii_login(self):
        req = self.request()
        user = self.create_user(req, login=u'françois')
        self.commit()
        req = self.request()
        with self.assertRaises(ValidationError):
            req.create_entity('SshPubKey',
                              data=Binary('42'),
                              reverse_public_key=user)

    def _test_permission_prologue(self):
        access_key = self.user().public_key[0]
        perm = self.admin_user_repo.reverse_granted_on[0]
        self._assert_end_of_prologue(access_key, perm)
        req = self.request()
        return req.entity_from_eid(access_key.eid), req.entity_from_eid(perm.eid)

    def _assert_end_of_prologue(self, access_key, perm):
        # Testing addition
        pubkey = self._hgadmin_file_content('keys', self.server_config.keys_subdir,
                                            self.user().login, str(access_key.eid))
        self.assertEqual(pubkey, 'admin public key')

        # Check access.conf content
        content = self._hgadmin_file_content(self.server_config.conf_filename)
        self.assertEqual(content,
                         'write user=cw/%(login)s/%(key_eid)d repo=admin_repo\n'
                         % {'login': self.user().login,
                            'key_eid': access_key.eid})

    def test_msc_regeration_service(self):
        access_key, perm = self._test_permission_prologue()

        userdesc = self.session.user.format_name_for_mercurial()
        msc = self.server_config
        with msc.exec_in_hgadmin_clone("pouette", user=userdesc) as hgrepo:
            commands.remove(hgrepo.ui, hgrepo,
                            osp.join(hgrepo.root, 'keys', msc.keys_subdir))
            filename = osp.join(hgrepo.root, msc.conf_filename_str)
            with open(filename, 'wb') as access:
                access.write('')
        self.vreg['services'].select('regenerate_hgadmin_repo', self.session).call(self.server_config.eid)
        self._assert_end_of_prologue(access_key, perm)

    def test_msc_deletion_ok(self):
        access_key, _perm = self._test_permission_prologue()
        self.execute('DELETE MercurialServerConfig X WHERE X eid %s' % self.server_config.eid)
        self.commit()

        # Check access.conf content
        content = self._hgadmin_file_content(self.server_config.conf_filename)
        self.assertEqual(content, '\n')

        with self.assertRaises(IOError):
            self._hgadmin_file_content('keys', self.server_config.keys_subdir,
                                       self.user().login, str(access_key.eid))

    def test_msc_deletion_with_rollback_inside(self):
        """ on deletion failure (i.e.: deletion order is issued
        but the trasnaction fails), the hgadmin repo files should
        be untouched -- though we may observe a pair of deletion commit/backout
        at the mercurial repository level
        """
        access_key, perm = self._test_permission_prologue()
        self.execute('DELETE MercurialServerConfig X WHERE X eid %s' % self.server_config.eid)
        self.rollback()

        self._assert_end_of_prologue(access_key, perm)

        # check that a 'backout' commit did happen
        hgrepo = hg.repository(mscui(), self.server_config.hgadmin_repopath)
        commands.log(hgrepo.ui, hgrepo)
        self.assertIn('backout', hgrepo.ui.popbuffer())

    def test_permission_AUD(self):
        """ Test Adding, Updating and Deleting """
        access_key, perm = self._test_permission_prologue()
        # Updating
        perm.cw_set(permission_level=u"write")
        self.commit() # Triggers hooks
        # Testing update
        # Check access.conf content
        content = self._hgadmin_file_content(self.server_config.conf_filename)
        self.assertEqual(content,
                         'write user=cw/%(login)s/%(key_eid)d repo=admin_repo\n'
                         % {'login': self.user().login,
                            'key_eid': access_key.eid,
                            })


        # Deleting the permission, thus the access_key relation
        perm.cw_delete()
        self.commit() # Triggers hooks
        #Check access.conf content
        content = self._hgadmin_file_content(self.server_config.conf_filename)
        self.assertEqual(content, '\n')


    def test_accesskey_AUD(self):
        """ Test Adding, Updating and Deleting"""
        access_key, perm = self._test_permission_prologue()

        # Updating
        access_key.cw_set(data=Binary('24'))
        self.commit() # Triggers hooks
        # Testing update
        pubkey = self._hgadmin_file_content('keys', 'cw',
                                            self.user().login, str(access_key.eid))
        self.assertEqual(pubkey, '24')

        # Deleting the key, thus the access_key relation
        access_key.cw_delete()
        self.commit() # Triggers hooks
        # Testing deletion
        with self.assertRaises(IOError) as exc :
            pubkey = self._hgadmin_file_content('keys', 'cw',
                                                self.user().login, str(access_key.eid))

        # Check access.conf content
        content = self._hgadmin_file_content(self.server_config.conf_filename)
        self.assertEqual(content, '\n')


    def test_consistent_permissions(self):
        """ Test at most one permissions for any (key, repo) pair"""
        req = self.request()
        # Adding
        access_key = req.create_entity('SshPubKey',
                                       data=Binary('42'),
                                       reverse_public_key=self.user())
        perm = req.create_entity('MercurialServerPermission',
                                 permission_level=u'read',
                                 access_key=access_key,
                                 granted_on=self.admin_user_repo)
        self.commit() # Triggers hooks
        with self.assertRaises(ValidationError) as exc :
            # The relations access_key and repo are inlined ...
            perm = req.create_entity('MercurialServerPermission',
                                     permission_level=u'deny',
                                     access_key=access_key,
                                     granted_on=self.admin_user_repo)
            self.commit() # ... so are checked immediatly even without commit



class SchemaPermTC(MercurialServerTCMixin, CubicWebTC):

    def test_ordinary_user_AUD(self):
        toto = self.create_user(self.request(), u'toto')
        titi = self.create_user(self.request(), u'titi')
        self.commit()
        with self.userlogin('toto') as cnx:
            # toto cannot create a mercurial server config
            req = cnx.request()
            with self.assertRaises(Unauthorized):
                self.create_mercurial_server(req, 'for_toto')
        with self.userlogin('toto') as cnx:
            # without a public key, toto cannot create a hosted repository
            req = cnx.request()
            toto_repo = self.create_mercurial_repo(req, 'toto_repo')
            with self.assertRaises(ValidationError) as wraperr:
                toto_repo.cw_set(hosted_by=self.server_config)
            self.assertEqual({'hosted_by': 'To create a hosted repository, toto must have a public key'},
                             wraperr.exception.args[1])
        with self.userlogin('titi') as cnx:
            # user titi owns a Repository, but not hosted_by
            req = cnx.request()
            pubkey = req.create_entity('SshPubKey', data=Binary('titi public key'),
                                       reverse_public_key=titi.eid)
            cnx.commit()
            titi_repo = self.create_mercurial_repo(req, 'titi_repo')
            cnx.commit()
        with self.userlogin('toto') as cnx:
            req = cnx.request()
            pubkey = req.create_entity('SshPubKey',
                                       data=Binary('toto public key'),
                                       reverse_public_key=toto.eid)
            self.create_mercurial_repo(req, 'toto_repo',
                                       hosted_by=self.server_config)
            cnx.commit()
        content = self._hgadmin_file_content(self.server_config.conf_filename)
        self.assertListEqual(
            ['write user=cw/admin/%d repo=admin_repo' % self.admin_pubkey.eid,
             'write user=cw/toto/%d repo=toto_repo' % toto.public_key[0].eid],
            content.splitlines())
        pk = self._hgadmin_file_content('keys', self.server_config.keys_subdir,
                                        toto.login, str(pubkey.eid))
        self.assertEqual('toto public key', pk)
        self.execute('DELETE CWUser U WHERE U login "toto"')
        self.commit()
        content = self._hgadmin_file_content(self.server_config.conf_filename)
        # all info about toto is gone
        self.assertEqual(['write user=cw/admin/%d repo=admin_repo' %
                            self.admin_pubkey.eid],
                         content.splitlines())
        with self.assertRaises(IOError):
            self._hgadmin_file_content('keys', self.server_config.keys_subdir,
                                       toto.login, str(pubkey.eid))

    def test_delete_hosted_by_non_owner(self):
        # just make sure non-owners of a Repository cannot change its
        # hosted_by relation (as per schema permissions)
        toto = self.create_user(self.request(), u'toto')
        self.commit()
        with self.userlogin('toto') as cnx:
            req = self.request()
            repo = req.entity_from_eid(self.admin_user_repo.eid)
            self.assertNotIn(toto.eid, set(o.eid for o in repo.owned_by))
            config = repo.hosted_by[0]
            with self.assertRaises(Unauthorized):
                req.execute('DELETE R hosted_by C WHERE R eid %d,'
                            '   C eid %d' %
                            (self.admin_user_repo.eid, config.eid))
                self.commit()
        repo = self.request().entity_from_eid(self.admin_user_repo.eid)
        repopath = repo.source_url[7:]
        self.assertTrue(osp.exists(repopath))

    def test_repo_deletion_non_owner(self):
        # make sure non-owners cannot delete a repository (as per schema
        # permissions)
        toto = self.create_user(self.request(), u'toto')
        self.commit()
        self.login(u'toto')
        req = self.request()
        repo = req.entity_from_eid(self.admin_user_repo.eid)
        with self.assertRaises(Unauthorized):
            req.execute('DELETE Repository R WHERE R eid %d' %
                        self.admin_user_repo.eid)
            self.commit()
        repopath = repo.source_url[7:]
        self.assertTrue(osp.exists(repopath))


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
