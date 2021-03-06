# -*- coding: utf-8 -*-

import os
import re

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.template.defaulttags import CommentNode

try:
    from django.template import Lexer, Parser
    Engine = None
except ImportError:
    from django.template.base import Lexer, Parser
    from django.template.engine import Engine


STYLEGUIDE_ACCESS = getattr(settings, 'STYLEGUIDE_ACCESS',
                            lambda user: user.is_staff or user.is_superuser)
STYLEGUIDE_DEBUG = getattr(settings, 'STYLEGUIDE_DEBUG', settings.DEBUG)
STYLEGUIDE_CACHE_NAME = getattr(settings, 'STYLEGUIDE_CACHE_NAME',
                                'styleguide_components')
STYLEGUIDE_DIR_NAME = getattr(settings, 'STYLEGUIDE_DIR_NAME', 'styleguide')
STYLEGUIDE_IGNORE_FOLDERS = getattr(settings, 'STYLEGUIDE_IGNORE_FOLDERS',
                                    ('includes', ))
STYLEGUIDE_DOCFILE_NAME = getattr(settings, 'STYLEGUIDE_DOCFILE_NAME',
                                  '__doc__.html')

FILE_NAME_RE = re.compile('^\d{2}\-')


class Styleguide(object):
    """Main class which is delivered to template"""

    def __init__(self):
        self._modules = None
        self._components = None
        self._items = None
        self.current_module = None
        self._loader = StyleguideLoader()

    @property
    def modules(self):
        if self._modules is None:
            self._modules = []
            for name, data in self._loader.get_styleguide_components().items():
                module_id = name.replace(' ', '_')
                comps = [StyleguideComponent(c) for c in data['components']]
                module = {
                    'id': module_id,
                    'name': name,
                    'link': reverse("styleguide.module", args=(module_id, )),
                    'components': comps
                }
                self._modules.append(StyleguideModule(module))

        return self._modules

    @property
    def components(self):
        if self._components is None:
            self._components = []
            for module in self.modules:
                self._components += module.components

        return self._components

    @property
    def items(self):
        """
        :deprecated:
        For retro compatibility only
        """
        modules = OrderedDict()
        for name, data in self._loader.get_styleguide_components().items():
            modules[name] = data['components']

        return modules

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
    def template(self):
        return self._data['template']

    @property
    def doc(self):
        return self._data['doc']


class StyleguideModule(StyleguideComponent):

    @property
    def components(self):
        return self._data['components']


class StyleguideLoader(object):

    def _get_app_template_dirs(self):
        """
        Helper to get the `app_template_dirs` in different django versions
        -> tuple(string, string, ...)
        """
        try:
            # django 1.8
            from django.template.utils import get_app_template_dirs
            return get_app_template_dirs("templates")
        except ImportError:
            # django <= 1.7
            pass

        try:
            from django.template.loaders.app_directories import \
                app_template_dirs
            return app_template_dirs
        except ImproperlyConfigured:
            # Running outside django's environmement
            return ()

    def _get_template_dirs(self):
        """
        Returns all template folder from all installed apps
        -> tuple(string, string, ..)
        """

        # Based on: ("https://github.com/django/django/blob/master/django"
        #            "/template/loaders/app_directories.py")
        styleguide_template_dirs = []
        template_dirs = getattr(settings, 'TEMPLATE_DIRS', ())

        app_template_dirs = self._get_app_template_dirs()
        app_template_dirs += tuple(template_dirs)

        for app_template_dir in app_template_dirs:
            template_dir = os.path.join(app_template_dir, STYLEGUIDE_DIR_NAME)

            if os.path.isdir(template_dir):
                styleguide_template_dirs.append(template_dir)

        return tuple(styleguide_template_dirs)

    def get_styleguide_components(self):
        """
        Search for all templates files in `STYLEGUIDE_DIR_NAME` app_directories
        in all installed apps in the django project

        returns a dict with the folder name as the key and a list with all
        template files in that folder.

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
            'layout': {
                'id': 'layout',
                'name': 'layout',
                'doc': {},
                'link': 'styleguide/layout/'
                'components': [
                    { 'id': 'header', 'name': 'header', 'file_name': ... },
                    { 'id': 'footer', 'name': 'footer', 'file_name': ... },
                ]
            },
            'components': {
                'id': 'components',
                'name': 'components',
                'doc': {},
                'link': 'styleguide/components/'
                'components': [
                    { 'id': 'bar', 'name': 'bar', 'file_name': ... },
                    { 'id': 'list', 'name': 'list', 'file_name': ... },
                ]
            }
        ]
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

                    components = self._get_components_from_folder(root,
                                                                  dir_name)

                    ret[dir_name] = {
                        'id': dir_name,
                        'name': self._format_file_name(dir_name),
                        'components': components,
                        'link': 'styleguide/layout/',
                        'doc': self._get_docfile_from_folder(root, dir_name),
                    }

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
                if file_name == STYLEGUIDE_DOCFILE_NAME:
                    # Do not process the doc file
                    continue

                if not file_name.endswith('.html'):
                    # only template files
                    continue

                doc = self.get_doc_from_file(os.path.join(root, file_name))
                component_id = self._format_file_id(file_name)
                template_path = os.path.join(STYLEGUIDE_DIR_NAME, dir_name,
                                             file_name)
                url = reverse("styleguide.component", args=(dir_name,
                                                            component_id,))
                url = url.replace('%23', '#')  # @see: http://stackoverflow.com/questions/11165267/django-redirect-with-anchor-parameters#comment57154035_22109798

                component = {
                    'id': component_id,
                    'name': self._format_file_name(doc.get('name', file_name)),
                    'file_name': file_name,
                    'template': template_path,
                    'doc': doc,
                    'link': url
                }

                components.append(component)

        return components

    def _get_docfile_from_folder(self, root, dir_name):
        """returns a dict with all doc from the given folder"""
        ret = {}
        path_to_doc_file = os.path.join(root, dir_name,
                                        STYLEGUIDE_DOCFILE_NAME)

        if os.path.isfile(path_to_doc_file):
            with open(path_to_doc_file) as docfile:
                content = docfile.read()

            ret = self.parse_doc(content)

        return ret

    def _format_file_id(self, file_name):
        """returns a valid string which can be used in html id attribute"""
        return self._format_file_name(file_name).replace(' ', '-')

    def _format_file_name(self, file_name):
        """returns the file_name formatted to display"""

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
        lexer = Lexer(file_contents)
        tokens = lexer.tokenize()
        if Engine is not None:
            engine = Engine.get_default()
            parser = Parser(lexer.tokenize(), engine.template_libraries, engine.template_builtins, origin=None)
        else:
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
