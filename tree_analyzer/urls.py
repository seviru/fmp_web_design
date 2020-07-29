#!/usr/bin/env python3
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("cluster_explorer", views.cluster_explorer, name="cluster_explorer"),
    path("design_tree=custom/select_parameters", views.select_custom_parameters, name="select_custom_parameters"),
    path("design_tree=custom/results", views.design_custom_tree, name="design_custom_tree"),
    path("design_tree=custom/results/updated", views.update_custom_tree, name="update_custom_tree"),
    path("design_tree=<cluster_number>", views.design_tree, name="design_tree"),
]