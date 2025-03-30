from django.urls import path, include
from .views import (
    login_user,
    register_user,
    request_password_reset,
    confirm_password_reset
)

urlpatterns = [
    path('login/', login_user, name='login'),
    path('register/', register_user, name='register'),
    path('password-reset/', request_password_reset, name='password-reset-request'),
    path('password-reset/confirm/', confirm_password_reset, name='password-reset-confirm'),
]