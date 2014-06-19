# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.conf.urls import patterns, url


urlpatterns = patterns(
    'smart_raw_id_bl.admin',
    url(
        r'^label_view/(?P<app_name>[\w-]+)/(?P<model_name>[\w-]+)/multi/$',
        'label_view',
        {
            'multi': True,
            'template_object_name': 'objects',
            'template_name': 'admin/raw_id_fields/multi_label.html'
        },
        name="raw_id_multi_label"),
    url(
        r'^label_view/(?P<app_name>[\w-]+)/(?P<model_name>[\w-]+)/$',
        'label_view',
        {
            'template_name': 'admin/raw_id_fields/label.html'
        },
        name="raw_id_label"),
)