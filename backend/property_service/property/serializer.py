import os
from django.conf import settings
from rest_framework import serializers

from .models import Property,PropertyImage
class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id','image','createdAt','updatedAt']
        read_only_fields = ['createdAt','updatedAt']
        
class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True,read_only=True)
    class Meta:
        model = Property
        fields = '__all__'
        
class PropertySerializerCreate(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True,write_only=True,required=False)
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ['user_id']
        
    def create(self,validated_data):
        image_data = validated_data.pop('image',[])
        property_instance = Property.objects.create(**validated_data)
        for img in image_data:
            PropertyImage.objects.create(property=property_instance,**img)
        return property_instance
    
    def update(self,instance,validated_data):
        image_data = validated_data.pop('image',[])
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance.save()
        if image_data:
            PropertyImage.objects.filter(property=instance).delete()
            for img in image_data:
                PropertyImage.objects.create(property=instance,**img)
        return instance
    
