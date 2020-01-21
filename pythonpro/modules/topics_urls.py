from django.urls import path

from pythonpro.modules import topics_views

app_name = 'topics'
urlpatterns = [
    path('<slug:slug>/', topics_views.old_detail, name='detail_old'),
]
