# import mock
# import unittest


# class SystemTestCase(unittest.TestCase):

#     @mock.patch('fabtools.system.distrib_id')
#     def test_os_family_debian(self, distrib_id):
#         distrib_id.return_value = 'Debian'

#         from fabtools.system import distrib_family
#         self.assertEqual(distrib_family(), 'debian')

#     @mock.patch('fabtools.system.distrib_id')
#     def test_os_family_ubuntu(self, distrib_id):
#         distrib_id.return_value = 'Ubuntu'

#         from fabtools.system import distrib_family
#         self.assertEqual(distrib_family(), 'debian')

#     @mock.patch('fabtools.system.distrib_id')
#     def test_os_family_redhat(self, distrib_id):
#         distrib_id.return_value = 'RHEL'

#         from fabtools.system import distrib_family
#         self.assertEqual(distrib_family(), 'redhat')

#     @mock.patch('fabtools.system.distrib_id')
#     def test_os_family_centos(self, distrib_id):
#         distrib_id.return_value = 'CentOS'

#         from fabtools.system import distrib_family
#         self.assertEqual(distrib_family(), 'redhat')

#     @mock.patch('fabtools.system.distrib_id')
#     def test_os_family_fedora(self, distrib_id):
#         distrib_id.return_value = 'Fedora'

#         from fabtools.system import distrib_family
#         self.assertEqual(distrib_family(), 'redhat')
