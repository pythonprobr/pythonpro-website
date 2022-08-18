from django.urls import path

from pythonpro.discord import views

app_name = 'discord'
urlpatterns = [
    path('autorize', views.autorize, name='autorize'),
]
