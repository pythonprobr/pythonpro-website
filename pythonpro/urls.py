"""pythonpro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import (
    LogoutView, PasswordResetCompleteView, PasswordResetConfirmView,
    PasswordResetDoneView,
)
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView
from two_factor.urls import urlpatterns as tf_urls

import pythonpro.launch.views
from pythonpro.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('conta/logout/', LogoutView.as_view(), name='logout'),
    path('conta/reiniciar_senha', core_views.password_reset, name='password_reset'),
    path('conta/reiniciar_senha/ok', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('conta/reiniciar/<uidb64>/<token>/', PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('conta/reiniciar/ok', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('discourse/', include('pythonpro.discourse.urls')),
    path('modulos/', include('pythonpro.modules.module_urls')),
    path('secoes/', include('pythonpro.modules.sections_urls')),
    path('capitulos/', include('pythonpro.modules.chapters_urls')),
    path('topicos/', include('pythonpro.modules.topics_urls')),
    path('turmas/', include('pythonpro.cohorts.urls')),
    path('dashboard/', include('pythonpro.dashboard.urls')),
    path('', include(tf_urls)),
    path('', include('pythonpro.launch.urls')),
    path('', include('pythonpro.core.urls')),
    path('', include('pythonpro.checkout.urls')),
    path('r/', include('pythonpro.redirector.urls')),
    path('p/', include('pythonpro.pages.urls')),
    path('checkout/', include('django_pagarme.urls')),
    path('inscricao', pythonpro.launch.views.member_landing_page, name='member_landing_page'),

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

if not settings.AWS_ACCESS_KEY_ID:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
if settings.DEBUG:
    import debug_toolbar

    urlpatterns.append(path('__debug__/', include(debug_toolbar.urls)))
