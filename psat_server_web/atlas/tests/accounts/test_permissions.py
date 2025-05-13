from django.contrib.auth.models import User, Permission, AnonymousUser
from django.test import TestCase

from accounts.permissions import has_write_permissions


class HasWritePermissionsTest(TestCase):

    def setUp(self):
        # Create a regular user without permission.
        self.user_without_perm = User.objects.create_user(
            username="noperm",
            password="password"
        )
        
        # Create a user with the "has_write_access" permission.
        self.user_with_perm = User.objects.create_user(
            username="perm",
            password="password"
        )
        permission = Permission.objects.get(codename='has_write_access')
        self.user_with_perm.user_permissions.add(permission)
        
        # Create a staff user.
        self.staff_user = User.objects.create_user(
            username="staff",
            password="password"
        )
        self.staff_user.is_staff = True
        self.staff_user.save()

    def test_unauthenticated_user(self):
        # An anonymous user should not have write permissions.
        anonymous = AnonymousUser()
        self.assertFalse(has_write_permissions(anonymous))

    def test_user_without_permission(self):
        # A regular authenticated user without the permission should not have write permissions.
        self.assertFalse(has_write_permissions(self.user_without_perm))

    def test_user_with_permission(self):
        # An authenticated user with the "has_write_access" permission should have write permissions.
        self.assertTrue(has_write_permissions(self.user_with_perm))

    def test_staff_user(self):
        # A staff user should have write permissions regardless of explicit permission.
        self.assertTrue(has_write_permissions(self.staff_user))