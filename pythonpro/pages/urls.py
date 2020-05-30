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
]
