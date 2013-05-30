import argparse
import unittest
import argparse_actions

class FolderExistsActionTest(unittest.TestCase):
    #
    # Support
    #
    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('directory', action=argparse_actions.FolderExistsAction)
        
    #
    # Tests
    #
    def folder_exists_test(self):
        command_line = ['/bin']
        options = self.parser.parse_args(command_line)
        self.assertEqual(options.directory, command_line[0])
        
    def folder_not_exist_test(self):
        command_line = ['/foo/bar/xyz']
        self.assertRaises(
            argparse_actions.NonFolderError,
            self.parser.parse_args,
            command_line
        )
        
    def remove_trailing_slash_test(self):
        command_line = ['/usr/bin/']
        expected_value = '/usr/bin'
        
        options = self.parser.parse_args(command_line)
        self.assertEqual(options.directory, expected_value)
        
    def multiple_existing_folders_test(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'directory', 
            nargs = 2,
            action=argparse_actions.FolderExistsAction)
        
        command_line = ['/bin', '/usr/bin']
        options = parser.parse_args(command_line)
        self.assertEqual(options.directory, command_line)
        
    def multiple_non_existing_folders_test(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'directory', 
            nargs = 2,
            action=argparse_actions.FolderExistsAction)
        
        command_line = ['/foo/bar/xyz', '/foo/bar/abc']
        self.assertRaises(
            argparse_actions.NonFolderError,
            parser.parse_args,
            command_line
        )
