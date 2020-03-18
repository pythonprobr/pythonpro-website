from django.urls import path

from . import views

app_name = 'checkout'
urlpatterns = [
    path('curso-de-python-intermediario', views.pytools_lp, name='pytools_lp'),
]
