from django.urls import path
from . import views

urlpatterns = [
    path('verify_otp/', views.VerifyOtpView.as_view(), name='verify_otp'),
]