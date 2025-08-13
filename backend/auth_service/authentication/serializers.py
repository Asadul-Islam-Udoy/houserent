from rest_framework import serializers
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from .models import Profile
import uuid
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)##validators=[validate_password]
    password2 = serializers.CharField(write_only=True)
    email= serializers.EmailField(required=False,allow_blank=True)
    phone= serializers.CharField(required=False,allow_blank=True)
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','phone','password','password2','is_active','email_verified_at']
   
   
    def validate(self,attrs):
        email = attrs.get('email')
        phone = attrs.get('phone','')
        first_name = attrs.get('first_name', '')
        last_name = attrs.get('last_name', '')
        
        if not email and not phone:
            raise serializers.ValidationError({"message":"Either email or phone is required"})
       
        if not email:
            attrs['email'] =  f"no-email-{first_name}{last_name}{uuid.uuid4().hex[:6]}".lower()
       
        if not phone :
            attrs['phone'] =  f"no-phone-{uuid.uuid4().hex[:6]}"  
        
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password":"Password is not match!"})
        return attrs
        
    def create(self,validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(
            email = validated_data['email'],
            password=validated_data['password'],
            username=validated_data.get('username',''),
            phone=validated_data['phone'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name']
        )
        if not user.username:
            user.username = f"{user.first_name}{user.last_name}".lower()
        user.set_password(validated_data['password'])
        user.save()
        Profile.objects.create(user=user)
        return user 
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
       model = Profile
       fields = '__all__'
       
    def update(self,instance,validated_data):
        user_data = validated_data.pop("user",None)
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance.save()
        if user_data:
            for attr,value in validated_data.items():
                setattr(instance,attr,value)
            instance.save()
        return instance
    
class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        exclude = ['password']
        
  
class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)
    
    def validate(self,attrs):
        email_or_phone = attrs.get('email_or_phone').strip()
        password = attrs.get('password')
        
        if not email_or_phone or not password:
            raise serializers.ValidationError("email/phone or password required!")
        
        user = User.objects.filter(models.Q(email=email_or_phone) | models.Q(phone=email_or_phone)).first()
    
        if not user:
           raise serializers.ValidationError("Invalid credentials.")
        
        if not user.check_password(password):
           raise serializers.ValidationError("Invalid password!")
       
        if not user.is_active:
           raise serializers.ValidationError("Accound is not active")
        
        Profile.objects.get_or_create(user=user)
        
        refresh = RefreshToken.for_user(user)
        return{
             "refresh": str(refresh),
            "access": str(refresh.access_token),
             "user": UserSerializer(user).data
        }
   
class ForgetPasswordVerifySerializer(serializers.Serializer):
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    new_comfirm_password = serializers.CharField(write_only=True)
    def validate(self,attrs):
        otp = attrs.get('otp')
        new_password = attrs.get('new_password')
        new_confrim_password = attrs.get('new_comfirm_password')
        
        if new_password != new_confrim_password:
            raise serializers.ValidationError("New password and confirm password do not match.")
        user = User.objects.filter(otp=otp).first()
        if not user:
             raise serializers.ValidationError("Invalid user OTP.")
        if user.otp_expires and user.otp_expires > timezone.now():
            raise serializers.ValidationError("OTP time is expires")
        self.user = user
        return attrs
    
    def save(self):
        user  = self.user
        user.password = make_password(self.validated_data['new_password'])
        user.otp = None
        user.otp_expires = None
        user.save()
        return user
            
    


