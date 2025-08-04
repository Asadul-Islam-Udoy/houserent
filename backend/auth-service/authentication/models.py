from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.utils import timezone
from django.db import models
from datetime import timedelta
import random

class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active',True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self.create_user(email,password,**extra_fields)


class CustomUser(AbstractBaseUser,PermissionsMixin):
    username = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True,max_length=255, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=True, null=True,unique=True)
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    otp = models.CharField(max_length=7,blank=True,null=True)
    otp_expires = models.DateTimeField(blank=True,null=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()
    
    def __str__(self):
            return self.username or self.email
        
    def set_otp(self):
        self.otp = str(random.randint(100000,999999))
        self.otp_expires = timezone.now()+timedelta(minutes=5)
        self.save()
        
    def verify_otp(self,otp_input):
        if self.otp == otp_input and self.otp_expires > timezone.now():
           return True 
        return False

    