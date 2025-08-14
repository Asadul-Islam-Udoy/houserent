from django.shortcuts import render
from rest_framework import viewsets,permissions,status,mixins
from .simplejwt import JWTUserlessAuthentication
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .serializer import PropertySerializer,PropertyImageSerializer,PropertySerializerCreate
from .models import Property
from .permission import IsOwnerOrAdmin
# Create your views here.
class PropertyViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = Property.objects.all().order_by('-createdAt')
    authentication_classes = [JWTUserlessAuthentication]

    def get_serializer_class(self):
        if self.action in ['create','update','partial_update']:
            return PropertySerializerCreate
        return PropertySerializer
    
    def get_permissions(self):
        if self.action in ['create','update','partial_update','destroy']:
            return [permissions.IsAuthenticated(),IsOwnerOrAdmin()]
        return [permissions.AllowAny()]
    
    def perform_create(self,serializer):
        serializer.save(user_id = self.request.user.id)
        
  