from rest_framework_simplejwt.authentication import JWTAuthentication

class JWTUserlessAuthentication(JWTAuthentication):
    """
    Authenticate JWT without fetching a User from local DB.
    """
    def get_user(self, validated_token):
        """
        Return a simple user-like object with only `id`.
        """
        user_id = validated_token.get('user_id') or validated_token.get('id')
        if not user_id:
            return None
        
        class SimpleUser:
            def __init__(self, user_id):
                self.id = user_id
                self.is_authenticated = True
        return SimpleUser(validated_token['user_id'])
