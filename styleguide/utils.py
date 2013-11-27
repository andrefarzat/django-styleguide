# -*- coding: utf-8 -*-

import os
import re
from collections import OrderedDict
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.template import Lexer, Parser
from django.template.defaulttags import CommentNode

STYLEGUIDE_DIR_NAME = 'styleguide'

STYLEGUIDE_URL = reverse("styleguide.index")

FILE_NAME_RE = re.compile('^\d{2}\-')


class StyleguideLoader(object):


    def _get_template_dirs(self):
        """
        Returns all template folder from all installed apps
        -> tuple(string, string, ..)
        """

        # Base on: https://github.com/django/django/blob/master/django/template/loaders/app_directories.py
        styleguide_template_dirs = []

        try:
            from django.template.loaders.app_directories import app_template_dirs
        except ImproperlyConfigured:
            # Running outside django's environmement
            app_template_dirs = []

        for app_template_dir in app_template_dirs:
            template_dir = os.path.join(app_template_dir, STYLEGUIDE_DIR_NAME)

            if os.path.isdir(template_dir):
                styleguide_template_dirs.append(template_dir)

        return tuple(styleguide_template_dirs)


    def get_styleguide_components(self):
        """
        Search for all templates files in `STYLEGUIDE_DIR_NAME` app_directories
        in all installed apps in the django project

        returns a dict with the folder name as the key and a list with all template
        files in that folder.

        for example, givin the following folder structure:

        /templates
          /styleguide
            /layout
              /header.html
              /footer.html
            /components
              /bar.html
              /list.html

        Would result in the following dict:

        {
            'layout' : [
                { 'name': 'header', 'file_name': 'header.html', 'template' : 'styleguide/layout/header.html', ... },
                { 'name': 'footer', 'file_name': 'footer.html', 'template' : 'styleguide/layout/footer.html', ... },
            ],
            'components' : [
                'name': 'bar', 'file_name': 'bar.html', 'template' : 'styleguide/components/bar.html', ... },
                'name': 'list', 'file_name': 'list.html', 'template' : 'styleguide/components/list.html', ... },
            ]
        }
        """

        ret = OrderedDict()
        styleguide_template_dirs = self._get_template_dirs()

        for styleguide_template_dir in styleguide_template_dirs:
            for root, dirs, files in os.walk(styleguide_template_dir):
                # To make it walk alphabetically
                dirs.sort()

                for dir_name in dirs:
                    ret[dir_name] = self._get_components_from_folder(root, dir_name)

        return ret


    def _get_components_from_folder(self, root, dir_name):
        """
        :root: The whole path to the folder
        :dir_name: The folder's name

        -> dict
        """

        components = []
        for root, dirs, files in os.walk(os.path.join(root, dir_name)):
            # To make it walk alphabetically
            files.sort()

            for file_name in files:
                if not file_name.endswith('.html'):
                    # only template files
                    continue

                doc = self.get_doc_from_file(os.path.join(root, file_name))

                component = {
                    'name': self._format_file_name(doc.get('name', file_name)),
                    'file_name': file_name,
                    'template': os.path.join(STYLEGUIDE_DIR_NAME, dir_name, file_name),
                    'doc': doc,
                    'link': reverse("styleguide.component", args=(dir_name, file_name.replace('.html', ''),))
                }

                components.append(component)

        return components


    def _format_file_name(self, file_name):
        """
        returns the file_name formatted to display
        """

        # if the file_name startswith two digits, remove them
        file_name = FILE_NAME_RE.split(file_name)[-1]
        return file_name.split('.html')[0].replace('_', ' ')


    def get_doc_from_file(self, file_path):
        """
        :file_path: string
        -> dict
        """

        doc_string = self.extract_doc_from_file(file_path)
        return self.parse_doc(doc_string)


    def extract_doc_from_file(self, file_path):
        """ -> string """

        file_contents = open(file_path).read()
        lexer = Lexer(file_contents, None)
        tokens = lexer.tokenize()
        parser = Parser(lexer.tokenize())

        index = 0
        result = ""

        for node in parser.parse():
            if isinstance(node, CommentNode):
                result = tokens[index+1].contents.strip()
                break

            index += 1

        return result


    def parse_doc(self, doc):
        """
        :doc: string
        parses the given string and returns a dict with all documentation tags
        -> dict
        """

        lines = doc.split("\n")
        current_tag = None
        ret = {}

        for line in lines:
            line = line.strip()

            if line.startswith('@doc'):
                continue

            if not line:
                continue

            if line and line[0] == '@':
                words = line.split(' ')
                current_tag = words[0][1:]
                ret[current_tag] = " ".join(words[1:]).strip()

            elif current_tag in ret:
                if ret[current_tag] != '':
                    ret[current_tag] += "\n"

                ret[current_tag] += "%s" % line

        return ret