from django.utils.unittest import TestCase


class PackageTestCase(TestCase):
    def setUp(self):
        pass
        # uid = str(uuid.uuid4())[0:8]
        # self.fs = FileSystem.objects.create(mount_point=('/tmp/cvmfs-%s' % uid))
        # self.project = Project(file_system=self.fs, directory='project')
        # os.makedirs(self.fs.mount_point)

    def test_statuses(self):
        pass

    def test_filepath(self):
        pass
        # file = open(os.path.join(self.project.full_path(), 'filename.tar.gz'), 'w')
        # file.close()
        #
        # p = Package(project=self.project, file=file)
        #
        # self.assertEqual(p.filepath(), os.path.join())

    def test_filename(self):
        pass

    def test_get_file_list(self):
        pass

    def test_deploy(self):
        pass

    def test_remove(self):
        pass