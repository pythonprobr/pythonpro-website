from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView

from pythonpro.payments import views

app_name = 'payments'
urlpatterns = [
    path('obrigado', views.thanks, name='thanks'),
    path('curso-de-python-completo/obrigado', views.membership_thanks, name='membership_thanks'),
    path('curso-de-python-completo', login_required(views.old_member_landing_page), name='member_landing_page'),
    path('membro-checkout', views.member_checkout, name='member_checkout'),
    path('curso-completo/obrigado/', views.membership_thanks, name='membership_thanks'),
    path('membro/captura/', views.member_capture, name='member_capture'),
    path('membro/boleto/', views.membership_boleto, name='membership_boleto'),
    path('pargarme/notificacao/<int:user_id>', views.pagarme_notification, name='pagarme_notification'),
    path('membership/notification/<int:user_id>', views.membership_notification, name='membership_notification'),
    path('pargarme/notificacao', views.pagarme_anonymous_notification, name='pagarme_anonymous_notification'),
    path('membership/notificacao', views.membership_anonymous_notification, name='membership_anonymous_notification'),

    # unused pages
    path(
        'curso-de-python-intermediario-oto',
        RedirectView.as_view(url=reverse_lazy('member_landing_page')),
        name='client_landing_page_oto'
    ),
    path(
        'curso-de-python-intermediario-do',
        RedirectView.as_view(url=reverse_lazy('member_landing_page')),
        name='client_landing_page_do'
    ),
    path(
        'curso-de-python-intermediario',
        RedirectView.as_view(url=reverse_lazy('member_landing_page')),
        name='client_landing_page'
    ),
]
