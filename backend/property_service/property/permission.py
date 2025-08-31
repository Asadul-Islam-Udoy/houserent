from rest_framework import permissions



class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):   
        print("Request User:", request.user.id)
        print("Property owner:", obj.user_id)
        return (
            obj.user_id == getattr(request.user, "id", None)
            or getattr(request.user, "is_staff", False)
            or getattr(request.user, "is_superuser", False)
        )