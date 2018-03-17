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
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView, \
    PasswordResetDoneView, PasswordResetCompleteView
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('conta/login/', LoginView.as_view(), name='login'),
    path('conta/logout/', LogoutView.as_view(), name='logout'),
    path('conta/reiniciar_senha', PasswordResetView.as_view(), name='password_reset'),
    path('conta/reiniciar_senha/ok', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('conta/reiniciar/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('conta/reiniciar/ok', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('aperitivo/', include('pythonpro.promos.urls')),
    path('discourse/', include('pythonpro.discourse.urls')),
    path('modulos/', include('pythonpro.modules.module_urls')),
    path('secoes/', include('pythonpro.modules.sections_urls')),
    path('capitulos/', include('pythonpro.modules.chapters_urls')),
    path('', include('pythonpro.core.urls')),

]
