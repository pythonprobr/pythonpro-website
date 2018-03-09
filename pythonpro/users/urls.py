from django.contrib.auth.views import LoginView
from django.urls import path


app_name = 'users'
urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
]
