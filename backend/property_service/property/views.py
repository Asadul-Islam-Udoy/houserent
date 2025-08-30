from django.shortcuts import render
from rest_framework import viewsets,permissions,status,mixins
from .simplejwt import JWTUserlessAuthentication
from rest_framework.response import Response
# from django.core.cache import cache
from .utils.redis_cache.cache import cache_get,cache_set,cache_delete
from django.db.models.signals import pre_delete
from django.shortcuts import get_object_or_404
from .serializer import PropertySerializer,PropertySerializerCreate
from .models import Property
from .permission import IsOwnerOrAdmin
from .utils.rabbitmq import publish_message
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
    
    def list(self,request,*args,**kwargs):
        cache_key = "property_list"
        data = cache_get(cache_key)
        if data is not None:
            return Response({"message":"property getting redis successfully","data":data},status=status.HTTP_200_OK)
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset,many=True)
        data = serializer.data
        cache_set(cache_key,data,timeout=60)
        return Response({"message":"property getting successfully","data":data},status=status.HTTP_200_OK)
    
    # def perform_create(self,serializer):
    #     serializer.save(user_id = self.request.user.id)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        cache_key = f"property_{pk}"
        data = cache_get(cache_key)
        if not data:
            property_obj = get_object_or_404(Property, pk=pk)
            serializer = PropertySerializer(property_obj)
            data = serializer.data
            cache_set(cache_key, data, timeout=60)

        return Response(data)

    def perform_create(self, serializer):
        property_obj = serializer.save(user_id=self.request.user.id)
        # Publish to RabbitMQ
        publish_message("property_created", {"id": property_obj.id, "title": property_obj.title})
        # Invalidate cache
        cache_delete("property_list")

    def perform_update(self, serializer):
        property_obj = serializer.save()
        publish_message("property_updated", {"id": property_obj.id, "title": property_obj.title})
        cache_delete("property_list")
        cache_delete(f"property_{property_obj.id}")

    def perform_destroy(self, instance):
        property_id = instance.id
        instance.delete()
        publish_message("property_deleted", {"id": property_id})
        cache_delete("property_list")
        cache_delete(f"property_{property_id}")
  