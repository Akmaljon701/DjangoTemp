from django.urls import path
from core.users import views

urlpatterns = [
    # sms code register
    path('auth/send-code', views.user_send_code, name='user_send_code'),
    path('auth/verify-code', views.user_verify_code, name='user_verify_code'),

    path('auth/complete-registration', views.user_complete_registration, name='user_complete_registration'),
    path('auth/reset-password', views.user_reset_password, name='user_reset_password'),

    path('login/', views.user_login, name='user_login'),
]
