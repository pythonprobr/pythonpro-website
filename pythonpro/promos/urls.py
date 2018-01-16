from django.urls import path

from . import views

app_name = 'promos'
urlpatterns = [
    path('<slug:slug>', views.video, name='video')
]
