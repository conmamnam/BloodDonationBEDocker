from django.urls import path
from .views import UserLoginAPIView, VerifyOTPByEmailAPIView, UserResetPasswordAPIView, RegisterAccountAPIView

urlpatterns = [
    path('users/login/', UserLoginAPIView.as_view()),
    path('users/signup/', RegisterAccountAPIView.as_view()),
    path('verify/send-otp/', VerifyOTPByEmailAPIView.as_view()),
    path('verify/reset-password/', UserResetPasswordAPIView.as_view()),
]