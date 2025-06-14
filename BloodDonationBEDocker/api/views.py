import random
from datetime import datetime

from django.contrib.auth.models import User
from django.core.cache import cache

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api.services import send_otp_email


# Create your views here.

class UserLoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                return Response(
                    data={
                        'access_token': str(access_token),
                        'refresh_token': str(refresh),
                        'user_last_name': user.last_name,
                        'email': user.email,
                        'role': user.user_profile.role,
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response({'detail': 'Wrong password.'}, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterAccountAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        otp_code = request.data.get('otp')
        email = request.data.get('email')
        password = request.data.get('password')
        users = User.objects.filter(email=email).first()
        if users is None:
            otp_code_cache = cache.get(f'otp_{email}')
            if otp_code_cache is not None and str(otp_code) == str(otp_code_cache):
                username = f'user{datetime.now().strftime("%Y%m%d%H%M%S")}'
                new_user = User.objects.create_user(username=username, email=email, password=password)
                refresh = RefreshToken.for_user(new_user)
                access_token = refresh.access_token
                return Response(
                    data={
                        'access_token': str(access_token),
                        'refresh_token': str(refresh),
                        'user_id': new_user.id,
                        'user_last_name': new_user.last_name,
                        'email': new_user.email,
                        'role': new_user.user_profile.role,
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'detail': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

class UserResetPasswordAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        otp_code = request.data.get('otp')
        email = request.data.get('email')
        new_password = request.data.get('newPassword')
        try:
            user = User.objects.get(email=email)
            if str(otp_code) == str(cache.get(f'otp_{email}')):
                user.set_password(new_password)
                user.save()
                cache.delete(f'otp_{email}')
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'detail': 'Email not found.'}, status=status.HTTP_401_UNAUTHORIZED)


class VerifyOTPByEmailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            otp_code = random.randint(100000, 999999)
            cache.set(f'otp_{email}', otp_code, timeout=300)
            send_otp_email(email, otp_code)
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'Email not found.'}, status=status.HTTP_401_UNAUTHORIZED)


