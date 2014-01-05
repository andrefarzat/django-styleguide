# -*- coding: utf-8 -*-
 
from django.shortcuts import render
from django.core.cache import cache
from styleguide.utils import StyleguideLoader, STYLEGUIDE_DIR_NAME, STYLEGUIDE_DEBUG


def index(request):
    components = None
    if not STYLEGUIDE_DEBUG:
        components = cache.get('styleguide_components')

    if components is None:
        loader = StyleguideLoader()
        components = loader.get_styleguide_components()
        cache.set('styleguide_components', components, None)

    index_path = "%s/index.html" % STYLEGUIDE_DIR_NAME
    context = { 'styleguide': components }
    return render(request, index_path, context)


def module(request, module_name):
    return index(request)


def component(request, module_name, component_name):
    return index(request)
