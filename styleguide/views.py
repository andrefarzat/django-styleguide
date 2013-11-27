# -*- coding: utf-8 -*-
 
from django.shortcuts import render
from styleguide.utils import StyleguideLoader


def index(request):
    styleguide_loader = StyleguideLoader()
    styleguide_components = styleguide_loader.get_styleguide_components()

    context = { 'styleguide': styleguide_components }
    return render(request, "styleguide/index.html", context)


def module(request, module_name):
    return index(request)


def component(request, module_name, component_name):
    return index(request)
    