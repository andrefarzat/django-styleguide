# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns('styleguide.views',
    url(r'', 'index', name="styleguide.index"),
    url(r'(?P<module_name>\w+)/$', 'module', name="styleguide.module"),
    url(r'(?P<module_name>\w+)\#(?P<component_name>\w+)', 'component', name="styleguide.component"),
)
