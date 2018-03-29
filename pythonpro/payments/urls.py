from django.urls import path

from pythonpro.payments import views

app_name = 'payments'
urlpatterns = [
    path('opcoes/', views.options, name='options'),
    path('obrigado/', views.thanks, name='thanks'),
]
