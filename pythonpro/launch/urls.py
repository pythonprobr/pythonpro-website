from django.urls import path

from . import views

app_name = 'launch'
urlpatterns = [
    path('semana-do-programador-profissional/inscricao', views.landing_page, name='landing_page'),
    path('semana-do-programador-profissional/form', views.lead_form, name='lead_form'),
    path('semana-do-programador-profissional/obrigado', views.ty, name='ty'),
    path('semana-do-programador-profissional/aula-1', views.cpl1, name='cpl1'),
    path('semana-do-programador-profissional/aula-2', views.cpl2, name='cpl2'),
    path('semana-do-programador-profissional/aula-3', views.cpl3, name='cpl3'),
]
