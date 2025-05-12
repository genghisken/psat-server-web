from rest_framework.throttling import UserRateThrottle
   
class UserAdminRateThrottle(UserRateThrottle):
    
    def get_rate(self, request=None):
        # Check if a user is authenticated and is an admin.
        if request and hasattr(request, 'user') and (request.user.is_staff or request.user.is_superuser):
            # Use the admin scope.
            self.scope = 'admin'
        else:
            # Use the user scope.
            self.scope = 'user'
        
        # For either case, return the rate the usual way.
        return super().get_rate()
    
    def allow_request(self, request, view):
        # Determine the allowed request rate as we normally would during
        # the `__init__` call.
        self.rate = self.get_rate(request=request)
        self.num_requests, self.duration = self.parse_rate(self.rate)

        return super().allow_request(request, view)
