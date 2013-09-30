# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-styleguide',
    version='0.1.2',
    author=u'André Farzat',
    author_email='andrefarzat@gmail.com',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/django-styleguide/',
    license='LICENSE',
    description='Styleguide for django projects',
    long_description=open('README.md').read(),
    install_requires=["Django >= 1.4.3",],
    include_package_data=True,
    zip_safe=False,
)