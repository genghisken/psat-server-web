from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

from psdbapi.authentication import ExpiringTokenAuthentication
from accounts.models import GroupProfile


class TokenAuthenticationUserTests(TestCase):
    def setUp(self):
        self.week_group = Group.objects.create(name="Weekly Expiring")
        GroupProfile.objects.create(group=self.week_group, token_expiration_time=timedelta(weeks=1))
        self.no_group_user = User.objects.create_user(username="no_group_user", password="password")
        self.week_user = User.objects.create_user(username="week_user", password="password")
        self.week_user.groups.add(self.week_group)
        self.no_group_token = Token.objects.create(user=self.no_group_user)
        self.week_token = Token.objects.create(user=self.week_user)
        self.auth = ExpiringTokenAuthentication()

    def test_default_expiry_for_user_with_no_group(self):
        self.assertEqual(
            self.auth.authenticate_credentials(self.no_group_token.key),
            (self.no_group_user, self.no_group_token),
        )
        self.no_group_token.created = now() - timedelta(days=settings.TOKEN_EXPIRY + 1)
        self.no_group_token.save()
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate_credentials(self.no_group_token.key)

    def test_group_expiry_is_honoured(self):
        self.assertEqual(
            self.auth.authenticate_credentials(self.week_token.key),
            (self.week_user, self.week_token),
        )
        self.week_token.created = now() - timedelta(weeks=2)
        self.week_token.save()
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate_credentials(self.week_token.key)
