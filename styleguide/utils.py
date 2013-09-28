import os
from django.template.loaders.app_directories import Loader, app_template_dirs

# Base on: https://github.com/django/django/blob/master/django/template/loaders/app_directories.py

STYLEGUIDE_DIR_NAME = 'styleguide'

styleguide_template_dirs = []


for app_tempalte_dir in app_template_dirs:
    template_dir = os.path.join(app_tempalte_dir, STYLEGUIDE_DIR_NAME)

    if os.path.isdir(template_dir):
        styleguide_template_dirs.append(template_dir)


styleguide_template_dirs = tuple(styleguide_template_dirs)

class StyleguideLoader(Loader):


    def get_styleguide_components(self):
        ret = {}

        for styleguide_template_dir in styleguide_template_dirs:
            for root, dirs, files in os.walk(styleguide_template_dir):
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
            for file_name in files:
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

        return ".".join(file_name.split('.html')[:-1])