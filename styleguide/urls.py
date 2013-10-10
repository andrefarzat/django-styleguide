# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from styleguide.views import index

urlpatterns = patterns('',
    url(r'', index, name="styleguide.index"),
)
