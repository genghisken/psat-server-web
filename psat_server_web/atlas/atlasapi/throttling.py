from rest_framework.throttling import UserRateThrottle

   
class UserAdminRateThrottle(UserRateThrottle):
    
    def get_rate(self):
        # Check if a user is authenticated and is an admin.
        if self.request and hasattr(self.request, 'user') and self.request.user.is_staff:
            # Use the admin scope.
            self.scope = 'admin'
        else:
            # Use the user scope.
            self.scope = 'user'
        
        # For either case, return the rate the usual way.
        return super().get_rate()
