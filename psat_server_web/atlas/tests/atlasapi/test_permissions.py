from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile

class TestPermissionsSetup(TestCase):   
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create groups
        self.read_group = Group.objects.create(name="Read Only")
        GroupProfile.objects.create(
            api_write_access=False,
            group=self.read_group, 
            token_expiration_time=timedelta(days=365)
        )
        self.write_group = Group.objects.create(name="Write Access")
        GroupProfile.objects.create(
            api_write_access=True,
            group=self.write_group, 
            token_expiration_time=timedelta(days=365)
        )
        # No GroupProfile for self.no_profile_group
        self.no_profile_group = Group.objects.create(name="No Profile")
    

class TestUserWritePermissions(TestPermissionsSetup):
    endpoint = "/api/vrascores/"

    def test_user_permissions_no_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with no group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User cannot access the POST endpoint
        """
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can't use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_permissions_read_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with read-only permissions on their group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User cannot access the POST endpoint
        """
        self.user.groups.add(self.read_group)
        self.user.save()
        
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can't use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_permissions_write_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with write permissions on their group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        self.user.groups.add(self.write_group)
        self.user.save()
        
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(self.endpoint)
        # This will now fail with a 400 because we're permitted but we've not 
        # provided the payload
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_permissions_no_group_profile(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with a group which does not have a group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User cannot access the POST endpoint
        - No critical failure should occur
        """
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can't use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestStaffWritePermissions(TestPermissionsSetup):
    endpoint = "/api/vrascores/"
    
    def setUp(self):
        super().setUp()
        self.user.is_staff = True
        self.user.save()
    
    def test_staff_permissions_no_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a staff user with no group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can use the post endpoint as we're staff. Again this is a 400 because
        # we've not provided the payload, but does show we have permission
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    def test_staff_permissions_read_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with read-only permissions on their group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        self.user.groups.add(self.read_group)
        self.user.save()
        
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can use the post endpoint as we're staff. Again this is a 400 because
        # we've not provided the payload, but does show we have permission
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_staff_permissions_write_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with write permissions on their group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        self.user.groups.add(self.write_group)
        self.user.save()
        
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(self.endpoint)
        # This will now fail with a 400 because we're permitted but we've not 
        # provided the payload
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_staff_permissions_no_group_profile(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with a group which does not have a group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        - No critical failure should occur
        """
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can use the post endpoint as we're staff. Again this is a 400 because
        # we've not provided the payload, but does show we have permission
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
class TestUserReadPermissions(TestPermissionsSetup):
    # Read only endpoint
    endpoint = "/api/vrascoreslist/"
    
    def setUp(self):
        super().setUp()
        
    def test_user_permissions_no_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with no group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_permissions_read_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with read-only permissions on their group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        self.user.groups.add(self.read_group)
        self.user.save()
        
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_permissions_write_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with write permissions on their group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        self.user.groups.add(self.write_group)
        self.user.save()
                
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Can use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_permissions_no_group_profile(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with a group which does not have a group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        - No critical failure should occur
        
        TODO: capture log output to check that an error is logged?
        """
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestStaffReadPermissions(TestPermissionsSetup):
    endpoint = "/api/vrascoreslist/"
    
    def setUp(self):
        super().setUp()
        self.user.is_staff = True
        self.user.save()
    
    def test_staff_permissions_no_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a staff user with no group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can use the post endpoint as we're staff
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    
    def test_staff_permissions_read_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with read-only permissions on their group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        self.user.groups.add(self.read_group)
        self.user.save()
        
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_staff_permissions_write_group(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with write permissions on their group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        """
        self.user.groups.add(self.write_group)
        self.user.save()
        
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Can use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_staff_permissions_no_group_profile(self):
        """Test whether permissions successfully allow or deny access to the API
        for a user with a group which does not have a group_profile.
        
        Expected behaviour:
        - User can access the GET endpoint
        - User can access the POST endpoint
        - No critical failure should occur
        """
        # Can always use the get endpoint
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Can use the post endpoint
        response = self.client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    