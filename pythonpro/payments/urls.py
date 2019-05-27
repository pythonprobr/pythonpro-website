from django.urls import path

from pythonpro.payments import views

app_name = 'payments'
urlpatterns = [
    path('opcoes/', views.options, name='options'),
    path('obrigado/', views.thanks, name='thanks'),
    path('pytools/obrigado/', views.pytools_thanks, name='pytools_thanks'),
    path('pytools/captura/', views.pytools_capture, name='pytools_capture'),
]
