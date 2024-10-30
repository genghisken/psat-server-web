# Write test to check if user has permission to view the page

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class TestPermissionsAuthenticated(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_permissions(self):
        endpoint = "/api/vrascores/"
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(endpoint)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.user.is_staff = True
        self.user.save()

        response = self.client.post(endpoint)
        # This will now fail with a 400 because we've not provided the payload
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)