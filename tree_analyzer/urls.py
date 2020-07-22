#!/usr/bin/env python3
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("cluster_explorer", views.cluster_explorer, name="cluster_explorer"),
    path("design_tree=<cluster_number>", views.design_tree, name="design_tree")
]