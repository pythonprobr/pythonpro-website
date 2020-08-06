from django.urls import path

from . import modules_views, sections_views, topics_views, chapters_views

app_name = 'modules'
urlpatterns = [
    path('', modules_views.index, name='index'),
    path('<slug:slug>/', modules_views.detail, name='detail'),
    path('enrol/<slug:slug>/', modules_views.enrol, name='enrol'),
    path('<slug:module_slug>/topicos/<slug:topic_slug>', topics_views.detail, name='topic_detail'),
    path('<slug:module_slug>/secoes/<slug:section_slug>', sections_views.detail, name='section_detail'),
    path('<slug:module_slug>/capitulos/<slug:chapter_slug>', chapters_views.detail, name='chapter_detail'),
    path('descricao/<slug:slug>/', modules_views.description, name='description'),
]
