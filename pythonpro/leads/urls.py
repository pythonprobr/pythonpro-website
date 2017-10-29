from django.urls import path

from . import views

app_name = 'leads'
urlpatterns = [
    path('', views.new, name='new'),
    path('registrado', views.subscribed, name='subscribed'),
]
