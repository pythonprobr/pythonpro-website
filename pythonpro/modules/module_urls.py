from django.urls import path

from . import modules_views, topics_views

app_name = 'modules'
urlpatterns = [
    path('', modules_views.index, name='index'),
    path('<slug:slug>/', modules_views.detail, name='detail'),
    path('<slug:module_slug>/topicos/<slug:topic_slug>', topics_views.detail, name='topic_detail'),
]
