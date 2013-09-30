import unittest
import os
from .utils import StyleguideLoader, STYLEGUIDE_DIR_NAME


CURRENT_PATH = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(CURRENT_PATH, '..')


class StyleguideLoaderTest(unittest.TestCase):

    def setUp(self):
        self.loader = StyleguideLoader()


    def test_format_name(self):

        # [ (given_file_name, expected_result), ... ]
        file_name_list_to_be_tested = [
            ("01-name.html", "name"),
            ("0-name.html", "0-name"),
            ("0x-name.html", "0x-name"),
            ("89-name.html", "name"),
            ("name.nothing.html", "name.nothing"),
            ("nothing.todo.no-where_to_go", "nothing.todo.no-where_to_go")
        ]


        for file_name, expected_result in file_name_list_to_be_tested:
            formatted_file_name = self.loader._format_file_name(file_name)
            self.assertEqual(formatted_file_name, expected_result)


    def test__get_components_from_folder(self):
        expected_result = [
            { 'file_name': u'footer.html', 'name': u'footer', 'template': u'styleguide/layout/footer.html'},
            { 'file_name': u'header.html', 'name': u'header', 'template': u'styleguide/layout/header.html'}
        ]

        path_to_test = os.path.join(PROJECT_ROOT, 'styleguide_mock', 'templates', STYLEGUIDE_DIR_NAME)
        result = self.loader._get_components_from_folder(path_to_test, 'layout')

        self.assertEqual(result, expected_result)


