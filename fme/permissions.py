from fme.models import User
from rest_framework import permissions

class RestrictedLoginPermission(permissions.BasePermission):
    message = "Only Administrators, Mentors, and Facilitators can log in to this system."

    def has_permission(self, request, view):
        # Allow OPTIONS requests (for pre-flight CORS requests)
        if request.method == 'OPTIONS':
            return True
            
        # Allow unauthenticated requests (they'll be handled by the view)
        if not request.user.is_authenticated:
            return True
            
        # Check if authenticated user has the right role
        return request.user.role in [
            User.Role.ADMIN,
            User.Role.MENTOR,
            User.Role.FACILITATOR
        ]
