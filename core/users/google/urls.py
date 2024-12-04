from django.urls import path
from core.users.google import views
from core.users.google import services

urlpatterns = [
    path('google-login/', views.GoogleLoginRedirectApi.as_view(), name='google-login-redirect'),
    path(services.CALLBACK_API_URL, views.GoogleLoginCallbackView.as_view(), name='google-login-callback'),
]