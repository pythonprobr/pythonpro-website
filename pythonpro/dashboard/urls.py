from django.urls import path

from . import views

app_name = 'dashboard'
urlpatterns = [
    path('topic_interaction', views.topic_interaction, name='topic_interaction'),
    path('', views.home, name='home'),
    path('certificados/<slug:module_slug>', views.certificate, name='certificate'),
]
