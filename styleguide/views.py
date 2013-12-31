# -*- coding: utf-8 -*-
 
from django.shortcuts import render
from styleguide.utils import StyleguideLoader, STYLEGUIDE_DIR_NAME


def index(request):
    styleguide_loader = StyleguideLoader()
    styleguide_components = styleguide_loader.get_styleguide_components()

    index_path = "%s/index.html" % STYLEGUIDE_DIR_NAME
    context = { 'styleguide': styleguide_components }
    return render(request, index_path, context)


def module(request, module_name):
    return index(request)


def component(request, module_name, component_name):
    return index(request)
