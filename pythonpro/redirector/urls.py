from django.urls import path

from pythonpro.redirector import views

app_name = 'redirector'
urlpatterns = [
    path('<slug:slug>', views.redirect, name='redirect'),
]
