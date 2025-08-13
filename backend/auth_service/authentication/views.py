
from django.db.models import Q
from django.utils import timezone
from .send_otp_sms import send_sms
from .send_otp_email import send_otp_email
from rest_framework import permissions,status,viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import RegisterSerializer,UserSerializer,LoginSerializer,ProfileSerializer,ForgetPasswordVerifySerializer
# Create your views here.

User = get_user_model()


# user register
class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]


    ##permission system register and verify_otp
    def get_permissions(self):
        if self.action in ['register', 'login', 'verify_user','forget_password','forget_password_verify']:
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    ##permission system register and verify_otp
    def get_authenticators(self):
        if getattr(self, 'action', None) in  ['register', 'login', 'verify_user','forget_password','forget_password_verify']:
            return []  
        return super().get_authenticators()
    
    ##register method
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
                    send_otp_email(existing_email)
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
                    if existing_phone.otp_expires and existing_phone.otp_expires > timezone.now():
                        return Response({"message":"OTP sented to your phone"},status=status.HTTP_200_OK)
                    existing_phone.set_otp()
                    send_sms(existing_phone)
                    return Response(
                        {"success": True, "message": "OTP re-sent to your phone"},
                        status=status.HTTP_200_OK,
                    )
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_otp()

        if email:
            send_otp_email(user)
            msg = "OTP sent to your email address."
        else:
            send_sms(user)
            msg = "OTP sent to your phone number."

        return Response({"success": True, "message": msg}, status=status.HTTP_201_CREATED)
        
    ## verify email otp method
    @action(detail=False,methods=['post'],permission_classes=[permissions.AllowAny])
    def verify_user(self,request):
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
    
    # login method
    @action(detail=False,methods=['post'],permission_classes=[permissions.AllowAny]) 
    def login(self,request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data,status=status.HTTP_200_OK)
    
    
    # profile update method
    @action(detail=False,methods=['patch'],permission_classes=[permissions.IsAuthenticated])
    def profile_update(self,request):
        try:
           pk = request.data.get('profile_id')
           if not pk:
               return Response({"message":"profile id not missing"},status=status.HTTP_404_NOT_FOUND) 
           user = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response({"message":"profile is not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"profile updated successfully!","profile":serializer.data},status=status.HTTP_200_OK)
        return Response({"message":"profile updated fail!",},status=status.HTTP_400_BAD_REQUEST)
    
    
    # email or phone update method
    @action(detail=False,methods=['post'],permission_classes=[permissions.IsAuthenticated])
    def email_or_phone_update(self,request):
        user = request.user
        new_contract = request.data.get('new_email_or_phone')
        if not new_contract:
           return Response({"message":"enter new email or phone!",},status=status.HTTP_400_BAD_REQUEST)
        user.set_otp()
        if '@' in new_contract:
            user.email = new_contract
            user.save()
            send_otp_email(user)
            msg = "Send OTP Your Email Address"
        else:
            if user.otp_expires and user.otp_expires > timezone.now():
                return Response({"message":"OTP sented to your phone"},status=status.HTTP_200_OK)
            user.phone = new_contract 
            user.save()
            send_sms(user)
            msg = "Send OTP Your Phone"  
        
        return Response({"success": True, "message": msg}, status=status.HTTP_200_OK) 

    
    
    # forget password method 
    @action(detail=False,methods=['post'],permission_classes=[permissions.AllowAny])
    def forget_password(self,request):
        email_or_phone = request.data.get('email_or_phone')
        user = User.objects.filter(Q(email=email_or_phone) | Q(phone=email_or_phone)).first()
        if not user:
           return Response({"message":"user is not exists!",},status=status.HTTP_400_BAD_REQUEST)
        user.set_otp()
        if '@' in user:
            send_otp_email(user)
            user.save()
            msg = "Send OTP Your Email Address"
        else:
            send_sms(user)
            user.save()
            msg = "Send OTP Your Phone Number"
        return Response({"success": True, "message": msg}, status=status.HTTP_200_OK) 


    #forget password verify method
    @action(detail=False,methods=['put'],permission_classes=[permissions.AllowAny])
    def forget_password_verify(self,request):
        serializer = ForgetPasswordVerifySerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "password reset successfully"}, status=status.HTTP_200_OK) 
        return Response({"success": False, "message": "password reset fail!"}, status=status.HTTP_400_BAD_REQUEST) 