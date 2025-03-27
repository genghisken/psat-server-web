from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APIRequestFactory

from atlasapi.throttling import UserAdminRateThrottle

dummy_rate_settings = {
    'DEFAULT_THROTTLE_RATES': {
        # For testing, use low limits.
        'user': '3/min',         
        'admin': '5/min',   
    }
}

class TestUserAdminThrottle(TestCase):
    def setUp(self):
        # Clear the cache to ensure tests start fresh.
        cache.clear()
        self.factory = APIRequestFactory()
        
        # Create a regular user.
        self.regular_user = User.objects.create_user(username='user', password='user')
        
        # Create an admin user.
        self.admin_user = User.objects.create_user(username='admin', password='admin')
        self.admin_user.is_staff = True
        self.admin_user.save()
        
        # Set the throttle scope used by the view.
        self.throttle_scope = 'admin'
        
        # A dummy view function for passing into allow_request.
        self.view = lambda request: None

    def test_regular_user_throttling(self):
        throttle = UserAdminRateThrottle()
        throttle.THROTTLE_RATES = dummy_rate_settings['DEFAULT_THROTTLE_RATES']
        
        request = self.factory.get('/dummy/')
        request.user = self.regular_user

        # Simulate three allowed requests.
        for i in range(3):
            allowed = throttle.allow_request(request, self.view)
            self.assertTrue(allowed, f"Request {i+1} should be allowed for regular user")
        
        # The fourth request should be throttled.
        allowed = throttle.allow_request(request, self.view)
        self.assertFalse(allowed, "4th request should be throttled for regular user")
        
    def test_admin_user_throttling(self):
        throttle = UserAdminRateThrottle()
        throttle.THROTTLE_RATES = dummy_rate_settings['DEFAULT_THROTTLE_RATES']
        
        request = self.factory.get('/dummy/')
        request.user = self.admin_user

        # Simulate five allowed requests.
        for i in range(5):
            allowed = throttle.allow_request(request, self.view)
            self.assertTrue(allowed, f"Admin request {i+1} should be allowed")
        
        # The sixth request should be throttled.
        allowed = throttle.allow_request(request, self.view)
        self.assertFalse(allowed, "6th request should be throttled for admin user")
