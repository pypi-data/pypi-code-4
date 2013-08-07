from django.test.testcases import TestCase
from ci.models import CiProject


class CiTestCase(TestCase):

    def setUp(self):
        self.ciproject = CiProject.objects.create(
            name="django-ci",
            url="https://freakypie@bitbucket.org/freakypie/django-ci.git",
            branch="master",
            test_commands="""
bin/python django-ci/subtestproject/manage.py test
"""
        )

    def testTest(self):
        self.ciproject.setup_venv()
#         self.ciproject.test()

    def tearDown(self):
        pass  # TODO: delete env
