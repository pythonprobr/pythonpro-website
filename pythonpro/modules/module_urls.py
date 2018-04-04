from django.urls import path

from . import modules_views

app_name = 'modules'
urlpatterns = [
    path('', modules_views.index, name='index'),
    path('<slug>/', modules_views.detail, name='detail'),

]
