from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .send_otp_phone import send_sms
from rest_framework import permissions,status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer,UserSerializer,LoginSerializer
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
        email = request.data.get('email')
        phone = request.data.get('phone')
        if email:
           existing_email = User.objects.filter(email=email).first()
           if existing_email:
                if existing_email.is_active:
                    return Response(
                        {"message": "Email is already registered"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    existing_email.set_otp()
                    send_mail(
                        subject="Your Register OTP Code",
                        message=f"Your OTP is {existing_email.otp}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[existing_email.email],
                        fail_silently=False,
                    )
                    return Response(
                        {"success": True, "message": "OTP re-sent to your email"},
                        status=status.HTTP_200_OK,
                    )
        if phone:         
            existing_phone = User.objects.filter(phone=phone).first()
            if existing_phone:
                if existing_phone.is_active:
                     return Response(
                        {"message": "Phone number is already registered"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    if existing_phone.otp_expires > timezone.now():
                        return Response({"message":"OTP sented to your phone"},status=status.HTTP_200_OK)
                    existing_phone.set_otp()
                    send_sms(existing_phone.phone, f"Your OTP is {existing_phone.otp}")
                    return Response(
                        {"success": True, "message": "OTP re-sent to your phone"},
                        status=status.HTTP_200_OK,
                    )
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_otp()

        if email:
            send_mail(
                subject="Your Register OTP Code",
                message=f"Your OTP is {user.otp}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            msg = "OTP sent to your email address."
        else:
            send_sms(user.phone, f"Your OTP is {user.otp}")
            msg = "OTP sent to your phone number."

        return Response({"success": True, "message": msg}, status=status.HTTP_201_CREATED)
        
    ## verify email otp
    @action(detail=False,methods=['post'],permission_classes=[permissions.AllowAny])
    def verify_email(self,request):
         email_or_phone = request.data.get('email_or_phone')
         input_otp = request.data.get('otp')
         if not email_or_phone or not input_otp:
             return Response({"message":"email or phone and OTP are required"},status=status.HTTP_400_BAD_REQUEST)
         try:
            user = User.objects.filter(email=email_or_phone).first()  
            if not user:
               user = User.objects.filter(phone=email_or_phone).first() 
            if not user:
                return Response({"message": "User is not found"}, status=status.HTTP_404_NOT_FOUND)
         except User.DoesNotExist:
             return Response({"message":"User is not found"},status=status.HTTP_404_NOT_FOUND)
         
         if user.verify_otp(input_otp):
            user.is_active = True
            user.email_verified_at = timezone.now()
            user.otp = None
            user.otp_expires = None
            user.save(update_fields=['otp', 'otp_expires', 'is_active', 'email_verified_at'])
             
            refresh = RefreshToken.for_user(user)
            return Response({"message":"OTP verify successfully","access_token":str(refresh.access_token),"refresh_token":str(refresh),"user":UserSerializer(user).data},status=status.HTTP_200_OK)
        
         return Response({"message":"Invalid or Expired OTP"},status=status.HTTP_400_BAD_REQUEST)
    # login
    @action(detail=False,methods=['post'],permission_classes=[permissions.AllowAny]) 
    def login(self,request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data,status=status.HTTP_200_OK)