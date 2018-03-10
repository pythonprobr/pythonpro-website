from django.urls import path

from pythonpro.discourse import views

app_name = 'discourse'
urlpatterns = [
    path('login/', views.sso, name='sso'),
]
