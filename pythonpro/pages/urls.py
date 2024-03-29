from django.urls import path

from pythonpro.pages import views
from django.views.generic.base import RedirectView


app_name = 'pages'
urlpatterns = [
    path(
        'webinario-carreira-pro/inscricao',
        views.CarreiraProLandingPage.as_view(),
        name='carreirapro_landing_page'
    ),
    path(
        'webinario-carreira-pro/obrigado',
        views.CarreiraProThankYouPage.as_view(),
        name='carreirapro_thank_you_page'
    ),
    path(
        'webinario-data-science/inscricao',
        views.DsWebinarLandingPage.as_view(),
        name='ds_webinar_landing_page'
    ),
    path(
        'webinario-data-science/obrigado',
        views.DsWebinarThankYouPage.as_view(),
        name='ds_webinar_thank_you_page'
    ),
    path(
        'lead-onboarding',
        views.LeadsOnboardingPage.as_view(),
        name='leads_onboarding_page'
    ),
    path(
        'bootcamp-pre-inscricao',
        views.BootcampVipLandingPage.as_view(),
        name='bootcamp_vip_landing_page'
    ),
    path(
        'bootcamp-pre-inscricao-obrigado',
        views.BootcampVipThankYouPage.as_view(),
        name='bootcamp_vip_thank_you_page'
    ),
    path(
        'rumo-a-primeira-vaga/inscricao-<str:date>_<str:version>',
        RedirectView.as_view(url="https://www.rumoaprimeiravaga.com.br"),
        name='tpp_webiorico_landing_page_date_page_var'
    ),
    path(
        'rumo-a-primeira-vaga/inscricao-<str:date>',
        RedirectView.as_view(url="https://www.rumoaprimeiravaga.com.br"),
        name='tpp_webiorico_landing_page_date_var'
    ),
    path(
        'rumo-a-primeira-vaga/inscricao',
        RedirectView.as_view(url="https://www.rumoaprimeiravaga.com.br"),
        name='tpp_webiorico_landing_page'
    ),
    path(
        'rumo-a-primeira-vaga/obrigado',
        RedirectView.as_view(url="https://www.rumoaprimeiravaga.com.br"),
        name='tpp_webiorico_thank_you_page'
    ),
    path(
        'gravacao-rumo-a-primeira-vaga/inscricao',
        RedirectView.as_view(url="https://www.rumoaprimeiravaga.com.br"),
        name='tpp_masterclass_landing_page'
    ),
    path(
        'gravacao-rumo-a-primeira-vaga/masterclass',
        RedirectView.as_view(url="https://www.rumoaprimeiravaga.com.br"),
        name='tpp_masterclass_thank_you_page'
    ),
    path(
        'pixeling/<str:endpoint>',
        views.PixelingPage.as_view(),
        name='pixeling'
    ),
]
