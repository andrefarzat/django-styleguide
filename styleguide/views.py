# -*- coding: utf-8 -*-
 
from django.shortcuts import render
from django.core.cache import cache
from styleguide.utils import Styleguide, STYLEGUIDE_DIR_NAME, STYLEGUIDE_DEBUG

def index(request):
    styleguide = None
    if not STYLEGUIDE_DEBUG:
        styleguide = cache.get('styleguide_components')

    if styleguide is None:
        styleguide = Styleguide()
        cache.set('styleguide_components', styleguide, None)

    context = { 'styleguide': styleguide }
    index_path = "%s/index.html" % STYLEGUIDE_DIR_NAME
    return render(request, index_path, context)


def module(request, module_name):
    return index(request)


def component(request, module_name, component_name):
    return index(request)
