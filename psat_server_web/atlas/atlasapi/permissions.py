from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsApprovedUser(BasePermission):
    def has_permission(self, request, view):
        # Allow all safe methods (GET, OPTIONS, HEAD)
        if request.method in SAFE_METHODS:
            return True
        
        # Only allow POST if the user is authenticated, active, and staff
        return (request.user 
                and request.user.is_authenticated 
                and request.user.is_staff)