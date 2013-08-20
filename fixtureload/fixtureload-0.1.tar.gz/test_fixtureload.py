import json
from testfixtures import TempDirectory, compare, ShouldRaise
import fixtureload

__author__ = 'ozanturksever'


class TestFixtureLoad:
    def setUp(self):
        self.d = TempDirectory()
        fixtureload.set_source_dir(self.d.path)
        self.d.write('test.json',
                json.dumps(
                    {
                        'description':
                            {
                                'samples': {
                                    'fixture0': {'a': 'b'},
                                    'fixture1': {'c': 'd'}
                                }
                            }
                    }
                ))
        self.d.write('test_corrupted.json', 'corrupted json')

    def tearDown(self):
        self.d.cleanup()

    def test_can_set_fixture_source_directory(self):
        fixtureload.set_source_dir('/tmp')
        assert fixtureload.fixture_source_dir == '/tmp'

    def test_can_load_fixture(self):
        fixture = fixtureload.load('test/description/fixture0')
        compare(fixture, {'a': 'b'})
        fixture = fixtureload.load('test/description/fixture1')
        compare(fixture, {'c': 'd'})

    def test_load_fixture_with_not_existed_file_should_raise(self):
        with ShouldRaise(IOError):
            fixtureload.load('not_existed/description/fixture0')

    def test_load_fixture_with_corrupted_file_should_raise(self):
        with ShouldRaise(ValueError):
            fixtureload.load('test_corrupted/description/fixture0')

    def test_parse_fixture_path(self):
        path = fixtureload.parse_fixture_path('test/desc/fixture0')
        compare(
            path,
            {
                'source_file': 'test.json',
                'fixture_desc': 'desc',
                'fixture': 'fixture0'
            }
        )

    def test_parse_fixture_path_if_path_is_not_valid(self):
        with ShouldRaise(ValueError('Fixture Path is not valid (testfixture0)')):
            fixtureload.parse_fixture_path('testfixture0')
