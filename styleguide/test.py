# -*- coding: utf-8 -*-

import unittest
import os

from django.core.urlresolvers import reverse

from .utils import StyleguideLoader, STYLEGUIDE_DIR_NAME


CURRENT_PATH = os.path.dirname(__file__)
PROJECT_ROOT = os.path.join(CURRENT_PATH, '..')
MOCK_PROJECT_PATH = os.path.join(PROJECT_ROOT, 'styleguide_mock', 'templates')
STYLEGUIDE_URL = reverse("styleguide.index")

DOC_STRING = """@doc

@name layout area
@description Nothing more than an area


""".strip()

DOC_STRING_2 = """@doc

@name something different
@oneline does this work ?
@twolines if I put this in
twolines, would this work ?
@threelines
  Now I am getting too deep ?
  I am going to write three lines !
  OMG! I did wrote three lines !!!

""".strip()


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
            ("nothing.todo.no-where-to-go", "nothing.todo.no-where-to-go"),

            # replacing underscore to whitespace
            ("name_separated", "name separated"),
            ("1_2_3_4_5_6", "1 2 3 4 5 6"),
            ('____A', "    A"),
        ]


        for file_name, expected_result in file_name_list_to_be_tested:
            formatted_file_name = self.loader._format_file_name(file_name)
            self.assertEqual(formatted_file_name, expected_result)


    def test__get_components_from_folder(self):
        expected_result = [
            { 'id': u'footer', 'file_name': u'footer.html', 'name': u'footer', 'template': u'styleguide/layout/footer.html', 'doc': {}, 'link': STYLEGUIDE_URL+'layout/footer' },
            { 'id': u'header', 'file_name': u'header.html', 'name': u'header', 'template': u'styleguide/layout/header.html', 'doc': {}, 'link': STYLEGUIDE_URL+'layout/header' }
        ]

        path_to_test = os.path.join(MOCK_PROJECT_PATH, STYLEGUIDE_DIR_NAME)
        result = self.loader._get_components_from_folder(path_to_test, 'layout')

        self.assertEqual(result, expected_result)


    def test_extract_doc_from_file(self):
        expected_result = DOC_STRING

        path_to_file = os.path.join(MOCK_PROJECT_PATH, STYLEGUIDE_DIR_NAME, 'components', '02-area.html')
        result = self.loader.extract_doc_from_file(path_to_file)

        self.assertEqual(result, expected_result)


    def test_parse_doc(self):
        expected_result = {
            'name': 'layout area',
            'description': 'Nothing more than an area'
        }

        result = self.loader.parse_doc(DOC_STRING)
        self.assertEqual(result, expected_result)

        expected_result = {
            "name": "something different",
            "oneline": "does this work ?",
            "twolines": "if I put this in\ntwolines, would this work ?",
            "threelines": "Now I am getting too deep ?\nI am going to write three lines !\nOMG! I did wrote three lines !!!"
        }

        result = self.loader.parse_doc(DOC_STRING_2)
        self.assertEqual(result, expected_result)