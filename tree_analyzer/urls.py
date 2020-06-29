from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("design_tree=<cluster_number>", views.design_tree, name="design_tree")
]