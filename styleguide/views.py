# -*- coding: utf-8 -*-

from django.core.cache import cache
from django.shortcuts import render
from django.http import Http404
from styleguide.utils import (Styleguide, STYLEGUIDE_DIR_NAME,
                              STYLEGUIDE_DEBUG, STYLEGUIDE_CACHE_NAME,
                              STYLEGUIDE_ACCESS)


def index(request, module_name=None, component_name=None):
    if not STYLEGUIDE_ACCESS(request.user):
        raise Http404()

    styleguide = None
    if not STYLEGUIDE_DEBUG:
        styleguide = cache.get(STYLEGUIDE_CACHE_NAME)

    if styleguide is None:
        styleguide = Styleguide()
        cache.set(STYLEGUIDE_CACHE_NAME, styleguide, None)

    if module_name is not None:
        styleguide.set_current_module(module_name)

    context = {'styleguide': styleguide}
    index_path = "%s/index.html" % STYLEGUIDE_DIR_NAME
    return render(request, index_path, context)
