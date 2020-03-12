from django.contrib.auth.decorators import login_required
from django.urls import path

from pythonpro.payments import views

app_name = 'payments'
urlpatterns = [
    path('obrigado', views.thanks, name='thanks'),
    path('curso-de-python-completo/obrigado', views.membership_thanks, name='membership_thanks'),
    path('curso-de-python-completo', login_required(views.old_member_landing_page), name='member_landing_page'),
    path('client-checkout', views.client_checkout, name='client_checkout'),
    path('membro-checkout', views.member_checkout, name='member_checkout'),
    path('lista-de-espera', views.waiting_list_ty, name='waiting_list_ty'),
    path('pytools/obrigado/', views.pytools_thanks, name='pytools_thanks'),
    path('curso-completo/obrigado/', views.membership_thanks, name='membership_thanks'),
    path('pytools/captura/', views.pytools_capture, name='pytools_capture'),
    path('membro/captura/', views.member_capture, name='member_capture'),
    path('pytools/boleto/', views.pytools_boleto, name='pytools_boleto'),
    path('membro/boleto/', views.membership_boleto, name='membership_boleto'),
    path('curso-de-python-intermediario-oto', views.client_landing_page_oto, name='client_landing_page_oto'),
    path('curso-de-python-intermediario-do', views.client_landing_page_do, name='client_landing_page_do'),
    path('curso-de-python-intermediario', views.client_landing_page, name='client_landing_page'),
    path('pargarme/notificacao/<int:user_id>', views.pagarme_notification, name='pagarme_notification'),
    path('membership/notification/<int:user_id>', views.membership_notification, name='membership_notification'),
    path('pargarme/notificacao', views.pagarme_anonymous_notification, name='pagarme_anonymous_notification'),
    path('membership/notificacao', views.membership_anonymous_notification, name='membership_anonymous_notification'),
]
