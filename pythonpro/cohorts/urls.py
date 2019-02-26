from django.urls import path

from pythonpro.cohorts import views

app_name = 'cohorts'
urlpatterns = [
    path('webinarios/', views.webinars, name='webinars'),
    path('webinarios/<slug:slug>/', views.webinar, name='webinar'),
    path('<slug:slug>/', views.detail, name='detail'),
]
