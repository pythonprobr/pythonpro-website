from django.urls import path

from . import views

app_name = 'checkout'
urlpatterns = [
    path('curso-de-python-intermediario', views.pytools_lp, name='pytools_lp'),
    path('curso-de-python-intermediario-oto', views.pytools_oto_lp, name='pytools_oto_lp'),
    path('inscricao', views.membership_lp, name='membership_lp'),
    path('lista-de-espera', views.waiting_list_ty, name='waiting_list_ty'),
]
