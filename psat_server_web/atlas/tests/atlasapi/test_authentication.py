# tests/test_authentication.py
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from atlasapi.authentication import ExpiringTokenAuthentication
from accounts.models import GroupProfile


class TokenAuthenticationTests(TestCase):

    def setUp(self):
        # Create groups
        self.week_group = Group.objects.create(name="Weekly Expiring")
        self.year_group = Group.objects.create(name="Yearly Expiring")
        self.never_expiring_group = Group.objects.create(name="Never Expiring")
        self.no_profile_group = Group.objects.create(name="No Profile")

        # Add expiration times to group profiles
        # No profile for self.no_profile_group
        GroupProfile.objects.create(group=self.week_group, token_expiration_time=timedelta(weeks=1))
        GroupProfile.objects.create(group=self.year_group, token_expiration_time=timedelta(days=365))
        GroupProfile.objects.create(group=self.never_expiring_group, token_expiration_time=timedelta(days=10000))

        # Create users and assign them to groups
        self.no_group_user = User.objects.create_user(username="no_group_user", password="password")
        self.no_profile_user = User.objects.create_user(username="no_profile_user", password="password")
        self.week_user = User.objects.create_user(username="week_user", password="password")
        self.year_user = User.objects.create_user(username="year_user", password="password")
        self.never_expiring_user = User.objects.create_user(username="never_expiring_user", password="password")

        # Assign users to groups
        # No group for self.no_group_user
        self.no_profile_user.groups.add(self.no_profile_group)
        self.week_user.groups.add(self.week_group)
        self.year_user.groups.add(self.year_group)
        self.never_expiring_user.groups.add(self.never_expiring_group)

        # Create tokens for each user
        self.no_group_token = Token.objects.create(user=self.no_group_user)
        self.no_profile_token = Token.objects.create(user=self.no_profile_user)
        self.week_token = Token.objects.create(user=self.week_user)
        self.year_token = Token.objects.create(user=self.year_user)
        self.never_expiring_token = Token.objects.create(user=self.never_expiring_user)

        # Setup token authentication
        self.auth = ExpiringTokenAuthentication()
        
    def test_no_group(self):
        # Test: user with no group profile should have default token expiration
        self.assertEqual(self.auth.authenticate_credentials(self.no_group_token.key), 
                         (self.no_group_user, self.no_group_token))
        
        self.no_group_token.created = now() - timedelta(days=settings.TOKEN_EXPIRY + 1)
        self.no_group_token.save()
        with self.assertRaises(AuthenticationFailed) as cm:
            self.auth.authenticate_credentials(self.no_group_token.key)
        self.assertEqual(str(cm.exception), 'Token has expired.')
        
    def test_no_profile(self):
        # Test: user with no group profile should have default token expiration
        with self.assertRaises(AuthenticationFailed) as cm:
            self.auth.authenticate_credentials(self.no_profile_token.key)
        self.assertEqual(str(cm.exception), 'Could not authenticate: Group has no profile. Please contact administrator.')

    def test_weekly_token_expiration(self):
        # Test: weekly expiring token should be valid if within one week
        self.assertEqual(
            self.auth.authenticate_credentials(self.week_token.key), 
            (self.week_user, self.week_token)
        )

        # Test: weekly token should expire after one week
        self.week_token.created = now() - timedelta(weeks=2)
        self.week_token.save()
        with self.assertRaises(AuthenticationFailed) as cm:
            self.auth.authenticate_credentials(self.week_token.key)
        self.assertEqual(str(cm.exception), 'Token has expired.')

    def test_yearly_token_expiration(self):
        # Test: yearly expiring token should be valid if within one year
        self.assertEqual(
            self.auth.authenticate_credentials(self.year_token.key), 
            (self.year_user, self.year_token)
        )

        # Test: yearly token should expire after one year
        self.year_token.created = now() - timedelta(days=400)
        self.year_token.save()
        with self.assertRaises(AuthenticationFailed) as cm:
            self.auth.authenticate_credentials(self.year_token.key)
        self.assertEqual(str(cm.exception), 'Token has expired.')

    def test_never_expiring_token(self):
        # Test: never-expiring token should always be valid
        self.assertEqual(
            self.auth.authenticate_credentials(self.never_expiring_token.key), 
            (self.never_expiring_user, self.never_expiring_token)
        )

        # Even if we artificially backdate the token, it should still be valid
        self.never_expiring_token.created = now() - timedelta(days=9999)
        self.never_expiring_token.save()
        self.assertEqual(
            self.auth.authenticate_credentials(self.never_expiring_token.key), 
            (self.never_expiring_user, self.never_expiring_token)
        )

