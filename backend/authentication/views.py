from django.shortcuts import render
from rest_framework import generics,permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer,UserSerializer
# Create your views here.

User = get_user_model()

class UserViewSet():
    pass
# user register
class RegisterView(APIView):
  pass
    
# user profile    
class ProfileView(APIView):
    permission_class = (permissions.IsAuthenticated)
    
    def get(self,request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)