#coding=utf8
from .base import BaseTestCase
from Acquisition import aq_parent
from OFS.Image import Image
from os.path import dirname, join
from prdg.plone.util import structure
from prdg.zope.permissions import add_local_role_to_user
from zExceptions import BadRequest
import pickle
import transaction
import unittest
from plone import api


module_path = dirname(__file__)
f = open(join(module_path, 'sample.png'))
image_data = f.read()
f.close()

SAMPLE_IMAGE = Image(
    'ofs_image_id',
    'ofs_image_title',
    image_data
)
SAMPLE_IMAGE.filename = 'ofs_image_filename.png'


class StructureTestCase(BaseTestCase):
    """Test the structure module."""

    def setUp(self):
        BaseTestCase.setUp(self)

        self.other_user_id = 'other_user'
        api.user.create(
            email='other_user@test.org',
            username=self.other_user_id,
        )

    def create_base_sample_dict(self, id_suffix=''):
        return {
            'portal_type': 'News Item',
            'id': 'sample_id' + id_suffix,
            'title': 'sample_title',
            'description': 'sample_description',
            'text': '<p>sample_text</p>',
        }

    def create_base_sample_obj(self, id_suffix=''):
        id = self.folder.invokeFactory(
            type_name='News Item',
            id='news_id' + id_suffix,
            title='news_title',
            text='news_text',
        )
        return self.folder[id]

    def test_create_obj_from_dict_basic(self):
        """Test create_obj_from_dict()."""
        container = self.folder

        d = self.create_base_sample_dict()
        obj = structure.create_obj_from_dict(container, d)
        self.fail_unless_dict_and_obj_matches(d, obj)

        # Trying to create with the same ID, should raise a BadRequest
        # exception.
        self.failUnlessRaises(
            BadRequest,
            structure.create_obj_from_dict,
            container,
            d
        )

    def test_create_obj_from_dict_workflow_dest_state(self):
        container = self.folder

        # Check with workflow_dest_state == initial state.
        d = self.create_base_sample_dict()
        d['workflow_dest_state'] = 'private'
        obj = structure.create_obj_from_dict(container, d)
        self.fail_unless_dict_and_obj_matches(d, obj)

        # Check with workflow_dest_state == 'published'
        d = self.create_base_sample_dict('_2')
        d['workflow_dest_state'] = 'published'
        obj = structure.create_obj_from_dict(container, d)
        self.fail_unless_dict_and_obj_matches(d, obj)

    def test_create_obj_from_dict_ref_field(self):
        container = self.folder

        ref_objs = [
            self.create_base_sample_obj('_2'),
            self.create_base_sample_obj('_3')
        ]

        d = self.create_base_sample_dict()
        d['ref:relatedItems'] = structure.objs_to_paths(ref_objs)
        obj = structure.create_obj_from_dict(container, d)
        self.fail_unless_dict_and_obj_matches(d, obj)

    def test_create_obj_from_dict_file_field(self):
        container = self.folder

        d = self.create_base_sample_dict()
        d['image'] = SAMPLE_IMAGE

        obj = structure.create_obj_from_dict(container, d)

        self.fail_unless_dict_and_obj_matches(d, obj)

        # Archetypes make the title attribute of the OFS.Image.Image be ignored.
        # The title attribute of the image on the image field is set to the
        # object's title. This assertion is pretty useless, but keep it here
        # to help we remember this odd behavior.
        self.failUnlessEqual(d['title'], obj.getImage().title)
        self.failIfEqual(d['image'].title, obj.getImage().title)

    def test_create_obj_from_dict_owner(self):
        container = self.folder

        d = self.create_base_sample_dict()
        d['owner_userid'] = self.other_user_id

        obj = structure.create_obj_from_dict(container, d)
        self.fail_unless_dict_and_obj_matches(d, obj)

    def test_create_dict_from_obj_basic(self):

        obj = self.create_base_sample_obj()
        d = structure.create_dict_from_obj(obj)
        self.fail_unless_dict_and_obj_matches(d, obj)

    def test_create_dict_from_obj_workflow_dest_state(self):

        obj = self.create_base_sample_obj()
        self.workflow.doActionFor(obj, 'publish')

        d = structure.create_dict_from_obj(obj)
        self.failUnless('workflow_dest_state' in d)
        self.fail_unless_dict_and_obj_matches(d, obj)

    def test_create_dict_from_obj_ref_field(self):

        obj = self.create_base_sample_obj()
        ref_objs = [
            self.create_base_sample_obj('_2'),
            self.create_base_sample_obj('_3')
        ]
        obj.setRelatedItems(ref_objs)

        d = structure.create_dict_from_obj(obj)
        self.failUnless('ref:relatedItems' in d)
        self.fail_unless_dict_and_obj_matches(d, obj)

    def test_create_dict_from_obj_owner(self):
        obj = self.create_base_sample_obj()

        d = structure.create_dict_from_obj(obj)
        self.failUnless('owner_userid' in d)
        self.fail_unless_dict_and_obj_matches(d, obj)

    def test_round_trip(self):

        container = self.folder

        d = self.create_base_sample_dict()
        obj = structure.create_obj_from_dict(container, d)
        d_from_obj = structure.create_dict_from_obj(obj)

        for (k, v) in d.iteritems():
            self.failUnlessEqual(v, d_from_obj[k])

    def _test_pickle(self, objs):
        """Assert the dicts created by this module are pickable."""
        container = aq_parent(objs[0])
        objs.append(container)

        query = {'path': '/'.join(container.getPhysicalPath())}

        dicts = list(structure.create_dict_for_all_objs(self.portal, query))
        pickle_str = pickle.dumps(dicts)
        dicts = pickle.loads(pickle_str)

        self.failUnlessEqual(len(dicts), len(objs))
        for d in dicts:
            obj = self.portal.unrestrictedTraverse('/'.join(d['_path']))
            self.fail_unless_dict_and_obj_matches(d, obj)

    def test_pickle_basic(self):
        """Assert the dicts created by this module are pickable."""
        objs = [
            self.create_base_sample_obj(),
            self.create_base_sample_obj(id_suffix='_2'),
        ]

        self._test_pickle(objs)

    def test_pickle_file_field(self):
        """
        Assert the dicts created by this module are pickable, with file field.
        """
        objs = [
            self.create_base_sample_obj(),
            self.create_base_sample_obj(id_suffix='_2'),
        ]
        objs[0].setImage(SAMPLE_IMAGE)

        self._test_pickle(objs)

    def _test_create_folders(self, context, path):
        folder = structure.create_folders(context, path)
        self.failUnlessEqual(folder.getId(), path[-1])

        test_path = context.getPhysicalPath()
        for folder_id in path:
            test_path += (folder_id,)
            folder = self.portal.unrestrictedTraverse('/'.join(test_path))
            self.failUnlessEqual(folder.getId(), folder_id)

    def test_create_folders(self):

        context = self.folder
        path = ('f1', 'f2', 'f3')
        self._test_create_folders(context, path)

        context = context[path[0]]
        path = path[1:] + ('f4',)
        self._test_create_folders(context, path)

    def test_create_dict_from_obj_image_field(self):
        """Check if create_dict_from_obj works correctly with image fields."""
        obj = self.create_base_sample_obj()
        obj.setImage(SAMPLE_IMAGE)
        transaction.commit()

        self.login_browser()
        self.browser.open(obj.absolute_url() + '/image_mini')
        old_image_mini = self.browser.contents

        d = structure.create_dict_from_obj(obj)
        image = d['image']

        # OFS.Image.File type is wrong !
        self.failUnless(isinstance(image, Image))

        self.failUnless(str(image.data))

        d['id'] += '2'
        obj2 = structure.create_obj_from_dict(self.folder, d)

        image = obj2.getImage()
        self.failUnless(image)

        tag = str(image).lower()
        self.failUnless('img' in tag)

        # See if PIL will raise an exception.
        obj2.getField('image').createScales(obj2)

        transaction.commit()

        # Functional tests.
        self.browser.open(obj2.absolute_url())
        self.failUnless('image_mini' in self.browser.contents)
        self.browser.open(obj2.absolute_url() + '/image_mini')
        self.failUnlessEqual(self.browser.contents, old_image_mini)
        self.fail_if_errors_in_error_log()

    def test_create_dict_from_obj_local_roles(self):
        obj = self.create_base_sample_obj('1')
        add_local_role_to_user(obj, 'Reviewer', 'AuthenticadedUsers')

        d = structure.create_dict_from_obj(obj)

        # This will check if the roles are the same.
        self.failUnless(d.get('local_roles'))
        self.fail_unless_dict_and_obj_matches(d, obj)

    def test_create_obj_from_dict_local_roles(self):
        d = self.create_base_sample_dict('1')
        d['local_roles'] = {'AuthenticadedUsers': ['Reviewer']}
        obj = structure.create_obj_from_dict(self.folder, d)

        # This will check if the roles are the same.
        self.fail_unless_dict_and_obj_matches(d, obj)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StructureTestCase))
    return suite
