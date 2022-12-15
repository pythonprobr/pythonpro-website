from django.urls import path

from pythonpro.cohorts import views

app_name = 'cohorts'
urlpatterns = [
    path('aulas/<int:pk>/', views.live_class, name='live_class'),
]
