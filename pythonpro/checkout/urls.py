from django.urls import path

from pythonpro.checkout import views
from django.views.generic.base import RedirectView

app_name = 'checkout'
urlpatterns = [
    path(
        'inscricao',
        RedirectView.as_view(url="https://pythonpro.com.br/bootcamp-devpro-matriculas-abertas/"),
        name='bootcamp_lp'
    ),
    path('bootcamp/inscricao-d1', views.bootcamp_lp_d1, name='bootcamp_lp_d1'),
    path('bootcamp/inscricao-djangopro-d1', views.bootcamp_lp_d1_webdev, name='bootcamp_lp_d1_webdev'),
    path('bootcamp/inscricao-d2', views.bootcamp_lp_d2, name='bootcamp_lp_d2'),
    path('bootcamp/inscricao-djangopro-d2', views.bootcamp_lp_d2_webdev, name='bootcamp_lp_d2_webdev'),
    path('bootcamp/inscricao-d3', views.bootcamp_lp_d3, name='bootcamp_lp_d3'),
    path('bootcamp/inscricao-djangopro-d3', views.bootcamp_lp_d3_webdev, name='bootcamp_lp_d3_webdev'),
    path('lista-de-espera', views.waiting_list_ty, name='waiting_list_ty'),
    path('curso-desenvolvimento-web-django-oto', views.webdev_landing_page_oto, name='webdev_landing_page_oto'),
    path(
        'curso-desenvolvimento-web-django-50-off', views.webdev_landing_page_50_off, name='webdev_landing_page_50_off'
    ),
    path(
        'curso-de-django',
        RedirectView.as_view(url="https://pythonpro.com.br/curso-djangopro/"),
        name='webdev_landing_page'
    ),
]
