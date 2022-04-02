from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('activate_account/', views.ActivateAccountView.as_view(), name='activate_account'),
    path('password_reset_request/', views.PasswordResetRequest.as_view(), name='password_reset_request'),
    path('password_reset', views.PasswordResetView.as_view(), name='my_password_reset')

]