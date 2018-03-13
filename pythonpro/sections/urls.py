from django.urls import path

from . import views

app_name = 'sections'
urlpatterns = [
    path('<slug:slug>/', views.detail, name='detail'),
]
