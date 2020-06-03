from django.urls import path

from pythonpro.checkout import views

app_name = 'checkout'
urlpatterns = [
    path('inscricao', views.membership_lp, name='membership_lp'),
    path('lista-de-espera', views.waiting_list_ty, name='waiting_list_ty'),
    path('curso-desenvolvimento-web-django', views.webdev_landing_page_oto, name='webdev_landing_page_oto'),
    path('curso-de-django', views.webdev_landing_page, name='webdev_landing_page'),
]
