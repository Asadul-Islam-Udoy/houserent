from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)##validators=[validate_password]
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','phone','password','password2']
   
   
    def validate(self,attrs):
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
        return user 
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']

        