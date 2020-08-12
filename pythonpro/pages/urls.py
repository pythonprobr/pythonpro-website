from django.urls import path

from pythonpro.pages import views


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
]
