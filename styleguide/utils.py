import os
import re
from collections import OrderedDict
from django.core.exceptions import ImproperlyConfigured

STYLEGUIDE_DIR_NAME = 'styleguide'
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
                { 'name': 'header', 'file_name': 'header.html', 'template' : 'styleguide/layout/header.html' },
                { 'name': 'footer', 'file_name': 'footer.html', 'template' : 'styleguide/layout/footer.html' },
            ],
            'components' : [
                'name': 'bar', 'file_name': 'bar.html', 'template' : 'styleguide/components/bar.html' },
                'name': 'list', 'file_name': 'list.html', 'template' : 'styleguide/components/list.html' },
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
        """

        components = []
        for root, dirs, files in os.walk(os.path.join(root, dir_name)):
            # To make it walk alphabetically
            files.sort()

            for file_name in files:
                if not file_name.endswith('.html'):
                    # only template files
                    continue

                component = {
                    'name': self._format_file_name(file_name),
                    'file_name': file_name,
                    'template': os.path.join(STYLEGUIDE_DIR_NAME, dir_name, file_name)
                }

                components.append(component)

        return components


    def _format_file_name(self, file_name):
        """
        returns the file_name formatted to display
        """

        # if the file_name startswith two digits, remove them
        file_name = FILE_NAME_RE.split(file_name)[-1]
        return file_name.split('.html')[0]
