from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTUserlessAuthentication(JWTAuthentication):
    """
    Authenticate JWT without fetching a User from local DB.
    """
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id') or validated_token.get('id')
        if not user_id:
            return None
        
        is_staff = validated_token.get("is_staff", False)
        is_superuser = validated_token.get("is_superuser", False)
        
        class SimpleUser:
            def __init__(self, user_id, is_staff=False, is_superuser=False):
                self.id = int(user_id)  # <-- convert to integer
                self.is_authenticated = True
                self.is_staff = is_staff
                self.is_superuser = is_superuser

            def __str__(self):
                return f"SimpleUser(id={self.id}, staff={self.is_staff}, superuser={self.is_superuser})"

        return SimpleUser(user_id=user_id, is_staff=is_staff, is_superuser=is_superuser)
