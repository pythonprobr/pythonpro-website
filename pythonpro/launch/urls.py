from django.urls import path

from . import views

app_name = 'launch'
urlpatterns = [
    path('semana-do-programador-profissional', views.landing_page, name='landing_page'),
    path('semana-do-programador-profissional/form', views.lead_form, name='lead_form'),
    path('semana-do-programador-profissional/obrigado', views.ty, name='ty'),
]
