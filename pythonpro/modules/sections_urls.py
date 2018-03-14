from django.urls import path

from pythonpro.modules import sections_views

app_name = 'sections'
urlpatterns = [
    path('<slug:slug>/', sections_views.detail, name='detail'),
]
