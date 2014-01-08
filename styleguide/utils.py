# -*- coding: utf-8 -*-

import os
import re
from collections import OrderedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.template import Lexer, Parser
from django.template.defaulttags import CommentNode


STYLEGUIDE_DEBUG = getattr(settings, 'STYLEGUIDE_DEBUG', settings.DEBUG)
STYLEGUIDE_CACHE_NAME = getattr(settings, 'STYLEGUIDE_CACHE_NAME', 'styleguide_components')
STYLEGUIDE_DIR_NAME = getattr(settings, 'STYLEGUIDE_DIR_NAME', 'styleguide')
STYLEGUIDE_IGNORE_FOLDERS = getattr(settings, 'STYLEGUIDE_IGNORE_FOLDERS', ('includes', ))

FILE_NAME_RE = re.compile('^\d{2}\-')


class Styleguide(object):
    """ Main class which is delivered to template """
    
    def __init__(self):
        self._modules = None
        self._items = None
        self.current_module = None
        self._loader = StyleguideLoader()


    @property
    def modules(self):
        if self._modules is None:
            self._modules = []
            for name, components in self._loader.get_styleguide_components().items():
                module_id = name.replace(' ', '_')
                module = {
                    'id': module_id,
                    'name': name,
                    'link': reverse("styleguide.module", args=(module_id, )),
                    'components': [StyleguideComponent(c) for c in components]
                }
                self._modules.append(StyleguideModule(module))

        return self._modules


    @property
    def components(self):
        ret = []
        for module in self.modules:
            ret += module.components

        return ret

    @property
    def items(self):
        """
        :deprecated: 
        For retro compatibility only
        """
        return self._loader.get_styleguide_components().items()


    @property
    def current_components(self):
        if self.current_module is None:
            return []
        else:
            return self.current_module.components


    def set_current_module(self, module_name):
        """ Sets the given module as the current one """
        for module in self.modules:
            if module.name == module_name:
                self.current_module = module
                break


    def is_index(self):
        """ If a module is defined as current, 
        we say that we are not in an index page """
        return self.current_module is None


class StyleguideComponent(dict):

    def __init__(self, data):
        self._data = data

    def __repr__(self):
        return self._data.__str__()

    def to_dict(self):
        return self._data

    @property
    def id(self):
        return self._data['id']

    @property
    def name(self):
        return self._data['name']

    @property
    def link(self):
        return self._data['link']

    @property
    def doc(self):
        return self._data['doc']


class StyleguideModule(StyleguideComponent):
    
    @property
    def components(self):
        return self._data['components']


class StyleguideLoader(object):


    def _get_template_dirs(self):
        """
        Returns all template folder from all installed apps
        -> tuple(string, string, ..)
        """

        # Based on: https://github.com/django/django/blob/master/django/template/loaders/app_directories.py
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
                { 'id': 'header', 'name': 'header', 'file_name': 'header.html', 'template' : 'styleguide/layout/header.html', ... },
                { 'id': 'footer', 'name': 'footer', 'file_name': 'footer.html', 'template' : 'styleguide/layout/footer.html', ... },
            ],
            'components' : [
                { 'id': 'bar', 'name': 'bar', 'file_name': 'bar.html', 'template' : 'styleguide/components/bar.html', ... },
                { 'id': 'list', 'name': 'list', 'file_name': 'list.html', 'template' : 'styleguide/components/list.html', ... },
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
                    if dir_name in STYLEGUIDE_IGNORE_FOLDERS:
                        continue
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
                component_id = self._format_file_id(file_name)

                component = {
                    'id': component_id,
                    'name': self._format_file_name(doc.get('name', file_name)),
                    'file_name': file_name,
                    'template': os.path.join(STYLEGUIDE_DIR_NAME, dir_name, file_name),
                    'doc': doc,
                    'link': reverse("styleguide.component", args=(dir_name, component_id,))
                }

                components.append(component)

        return components


    def _format_file_id(self, file_name):
        """
        returns a valid string which can be used in html id attribute
        """
        return self._format_file_name(file_name).replace(' ', '-')


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