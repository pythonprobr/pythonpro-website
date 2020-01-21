from django.urls import path

from pythonpro.modules import chapters_views

app_name = 'chapters'
urlpatterns = [
    path('<slug:chapter_slug>/', chapters_views.detail_old, name='detail_old'),
]
