from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsTransientObjects, TcsCrossMatchesExternal


class TestExternalCrossmatchesList(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='xmuser', password='testpassword')
        self.read_group = Group.objects.create(name="Read Access")
        GroupProfile.objects.create(api_write_access=False, group=self.read_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.read_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.transient = TcsTransientObjects.objects.create(id=900000004, ra_psf=13.0, dec_psf=-8.0, date_inserted=now())
        self.crossmatch = TcsCrossMatchesExternal.objects.create(
            id=900000001, transient_object_id_id=self.transient.id,
            external_designation='SN2026aa', matched_list='Test List',
        )

    def tearDown(self):
        TcsCrossMatchesExternal.objects.filter(transient_object_id=self.transient.id).delete()
        self.transient.delete()

    def test_returns_matches_for_known_designation(self):
        response = self.client.get('/api/externalxmlist/', {'externalObjects': 'SN2026aa'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0][0]['external_designation'], 'SN2026aa')

    def test_returns_empty_list_for_unknown_designation(self):
        response = self.client.get('/api/externalxmlist/', {'externalObjects': 'nonexistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
