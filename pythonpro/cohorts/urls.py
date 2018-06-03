from django.urls import path

from pythonpro.cohorts import views

app_name = 'cohorts'
urlpatterns = [
    path('<slug:slug>/', views.detail, name='detail'),
]
