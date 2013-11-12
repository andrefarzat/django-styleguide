# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from styleguide.views import index, module, component

urlpatterns = patterns('',
    url(r'', index, name="styleguide.index"),
    url(r'(?P<module_name>\w+)/$', module, name="styleguide.module"),
    url(r'(?P<module_name>\w+)/(?P<component_name>\w+)', component, name="styleguide.component"),
)
