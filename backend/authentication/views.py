from django.core.mail import send_mail
from django.conf import settings
from rest_framework import permissions,status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer,UserSerializer
# Create your views here.

User = get_user_model()


# user register
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    authentication_classes = []  

    ##permission system register and verify_otp
    def get_permissions(self):
        if self.action in ['register', 'verify_otp']:
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    ##permission system register and verify_otp
    def get_authenticators(self):
        if getattr(self, 'action', None) in ['register', 'verify_otp']:
            return []  
        return super().get_authenticators()

    ##register 
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_otp()

        send_mail(
          subject='Your Register OTP Code',
          message=f"Your OTP is {user.otp}",
          from_email=settings.DEFAULT_FROM_EMAIL,
          recipient_list=[user.email],
          fail_silently=False
         )

        return Response(
            {
                'success':True,
                'message': 'OTP sent to your email address',
                 
            },
            status=status.HTTP_201_CREATED
        )
        
    ## verify email otp
    @action(detail=False,methods=['post'],permission_classes=[permissions.AllowAny])
    def verify_email(self,request):
         email = request.data.get('email')
         input_otp = request.data.get('otp')
         if not email or not input_otp:
             return Response({"message":"Email and OTP are required"},status=status.HTTP_400_BAD_REQUEST)
         try:
           user = User.objects.get(email=email)  
         except User.DoesNotExist:
             return Response({"message":"User is not found"},status=status.HTTP_404_NOT_FOUND)
         
         if user.verify_otp(input_otp):
             user.otp = None,
             user.otp_expires = None,
             user.is_active = True
             user.save()
             
             refresh = RefreshToken.for_user(user)
             return Response({"message":"OTP verify successfully","access_token":str(refresh.access_token),"refresh_token":str(refresh),"user":UserSerializer(user).data},status=status.HTTP_200_OK)
         
         return Response({"message":"Invalid or Expired OTP"},status=status.HTTP_400_BAD_REQUEST)