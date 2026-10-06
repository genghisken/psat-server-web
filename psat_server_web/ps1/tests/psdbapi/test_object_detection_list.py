from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsTransientObjects


class TestObjectDetectionList(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='snoozeuser', password='testpassword')
        self.write_group = Group.objects.create(name="Write Access 3")
        GroupProfile.objects.create(api_write_access=True, group=self.write_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.write_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.transient = TcsTransientObjects.objects.create(
            id=900000005, ra_psf=14.0, dec_psf=-9.0, date_inserted=now(), detection_list_id_id=3,
        )

    def tearDown(self):
        self.transient.delete()

    def test_updates_detection_list_id(self):
        response = self.client.post('/api/objectdetectionlist/', {'objectid': self.transient.id, 'objectlist': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transient.refresh_from_db()
        self.assertEqual(self.transient.detection_list_id_id, 4)

    def test_rejects_missing_object(self):
        response = self.client.post('/api/objectdetectionlist/', {'objectid': 999999999, 'objectlist': 4})
        self.assertEqual(response.data['info'], 'Object does not exist.')
