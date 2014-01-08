# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('styleguide.views',
    url(r'^(?P<module_name>\w+)\#(?P<component_name>\w+)', 'index', name="styleguide.component"),
    url(r'^(?P<module_name>\w+)', 'index', name="styleguide.module"),
    url(r'', 'index', name="styleguide.index"),
)
