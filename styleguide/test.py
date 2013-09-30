import unittest
from .utils import StyleguideLoader


class SimpleTest(unittest.TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


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