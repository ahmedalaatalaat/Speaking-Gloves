from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth.models import User
from main.utils import get_object_or_none
from rest_framework.views import APIView
from rest_framework import status
from django.views import View
from .serializers import *
from random import sample
from .models import *
import json


class RegistrationView(APIView):
    def post(self, request):
        user = get_object_or_none(User, username=request.data.get('email'))
        if user:
            return Response({"code": 701, "error": "user already exists!"}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            my_user = User.objects.create_user(
                username=request.data.get('email'),
                password=request.data.get('password'),
                first_name=request.data.get('name'),
            )
            
            system_user = SystemUser.objects.create(
                phone=request.data.get('phone'),
                birthday=request.data.get('birthday'),
                image=request.FILES.get('image'),
                gender=request.data.get('gender'),
                user=my_user,
            )
            
            token = Token.objects.get(user=my_user)
            
            data = {
                "token": str(token),
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def get(self, request):
        serializer = LoginSerializer(data=request.query_params)
        if serializer.is_valid():
            user = get_object_or_none(User, username=request.query_params.get('email'))
            if not user:
                return Response({"code": 702, "error": "Invalid email or password"}, status=status.HTTP_403_FORBIDDEN)
            
            if user.check_password(request.query_params.get('password')):
                token = Token.objects.get(user=user)
            
                data = {
                    "token": str(token),
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({"code": 702, "error": "Invalid email or password"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
        system_user = SystemUser.objects.get(user=request.user)
        serializer = ProfileSerializer(system_user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            system_user = SystemUser.objects.get(user=request.user)
            system_user.phone = request.data.get('phone')
            system_user.gender = request.data.get('gender')
            system_user.birthday = request.data.get('birthday')
            system_user.user.first_name = request.data.get('name')
            
            if request.FILES.get('image'):
                system_user.image = request.FILES.get('image')
                
            system_user.save()
            system_user.user.save()
            serializer = ProfileSerializer(system_user, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetUserPassword(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def put(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.check_password(request.data.get('old_password')):
                request.user.set_password(request.data.get('new_password'))
                request.user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"code": 702, "error": "Invalid email or password"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignLanguageLessonView(APIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
        lessons = Lesson.objects.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

