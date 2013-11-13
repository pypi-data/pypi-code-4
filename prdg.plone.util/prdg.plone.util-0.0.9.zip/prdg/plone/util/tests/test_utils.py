import unittest
from prdg.plone.util import utils
from base import BaseTestCase


class UtilsTestCase(BaseTestCase):
    """Test the utils module."""

    def get_wf_info(self, obj):
        default_workflow = self.workflow.getChainFor(obj)[0]
        initial_state = getattr(self.workflow, default_workflow).initial_state

        return (default_workflow, initial_state)

    def test_get_workflow_transitions(self):
        """
        Test get_workflow_transitions() according with the default workflow.
        """
        id = self.folder.invokeFactory(type_name='Document', id='SomeID')
        obj = self.folder[id]

        (default_workflow, initial) = self.get_wf_info(obj)

        # Transitions from visible to published. The first one does not specify
        # the source state, then current is used.
        self.failUnlessEqual(
            utils.get_workflow_transitions(obj, dest='published'),
            set(['publish'])
        )
        self.failUnlessEqual(
            utils.get_workflow_transitions(obj, dest='published', source=initial),
            set(['publish'])
        )

        self.workflow.doActionFor(obj, 'publish')

        # Now from published to the initial state.
        self.failUnlessEqual(
            utils.get_workflow_transitions(obj, dest=initial),
            set(['reject', 'retract'])
        )
        self.failUnlessEqual(
            utils.get_workflow_transitions(obj, dest=initial, source='published'),
            set(['reject', 'retract'])
        )

    def do_test_ensure_workflow_state(self, obj, dest):
        utils.ensure_workflow_state(obj, dest)
        self.failUnless(utils.get_workflow_state(obj), dest)

    def test_ensure_workflow_state(self):
        id = self.folder.invokeFactory(type_name='Document', id='SomeID')
        obj = self.folder[id]
        initial = self.get_wf_info(obj)[1]

        # Make obj published.
        self.do_test_ensure_workflow_state(obj, 'published')

        # Now back to the initial state.
        self.do_test_ensure_workflow_state(obj, initial)

        # Again ... it should not fail.
        self.do_test_ensure_workflow_state(obj, initial)

        # See if error handling is working.
        self.failUnlessRaises(
            RuntimeError,
            self.do_test_ensure_workflow_state,
            obj, 'non-ecziste'
        )


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UtilsTestCase))
    return suite
