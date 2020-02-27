from django.urls import path
from django_sitemaps import robots_txt

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt', robots_txt(timeout=86400), name='robots'),
    path('tech-talks', views.teck_talks, name='tech_talks'),
    path('linktree', views.linktree, name='linktree'),
    path('podcast', views.podcast, name='podcast'),
    path('curso-de-python-gratis', views.lead_landing, name='lead_landing'),
    path('curso-de-python-gratis-lite', views.lead_landing_lite, name='lead_landing_lite'),
    path('cadastro-python-birds', views.lead_form, name='lead_form'),
    path('definir-senha', views.lead_change_password, name='lead_change_password'),
    path('obrigado', views.thanks, name='thanks'),
    path('perfil', views.profile, name='profile'),
    path('perfil/nome', views.profile_name, name='profile_name'),
    path('perfil/email', views.profile_email, name='profile_email'),
    path('perfil/senha', views.profile_password, name='profile_password'),
    path('lista-de-espera', views.waiting_list, name='waiting_list'),
]
