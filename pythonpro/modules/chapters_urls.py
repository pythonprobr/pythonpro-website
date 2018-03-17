from django.urls import path

from pythonpro.modules import chapters_views

app_name = 'chapters'
urlpatterns = [
    path('<slug:slug>/', chapters_views.detail, name='detail'),
]
