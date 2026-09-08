from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsTransientObjects, TcsForcedPhotometry
from psdb.apiutils import transientObjectApi


class TestTransientObjectApi(TestCase):
    def setUp(self):
        self.transient = TcsTransientObjects.objects.create(
            id=900000006, ra_psf=15.0, dec_psf=-10.0, date_inserted=now(), ps1_designation='PS26aa',
        )
        self.fp = TcsForcedPhotometry.objects.create(
            id=900000001, transient_object_id_id=self.transient.id, ra_psf=15.0, dec_psf=-10.0,
            mjd_obs=60000.0, fptype=0,
        )

    def tearDown(self):
        TcsForcedPhotometry.objects.filter(transient_object_id=self.transient.id).delete()
        self.transient.delete()

    def test_returns_object_and_forced_photometry(self):
        data = transientObjectApi(None, self.transient.id)
        self.assertEqual(data['object']['id'], self.transient.id)
        self.assertEqual(len(data['fp']), 1)
        self.assertEqual(data['fp'][0]['mjd_obs'], 60000.0)
        self.assertEqual(data['sherlock_crossmatches'], [])
        self.assertEqual(data['sherlock_classifications'], [])
        self.assertEqual(data['external_crossmatches'], [])
        self.assertEqual(data['tns_crossmatches'], [])

    def test_returns_empty_shell_for_unknown_object(self):
        data = transientObjectApi(None, 999999999)
        self.assertIsNone(data['fp'])
        self.assertIn('object', data)

    def test_mjd_threshold_filters_forced_photometry(self):
        data = transientObjectApi(None, self.transient.id, mjdThreshold=60001.0)
        self.assertEqual(data['fp'], [])


class TestObjectsEndpoint(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='objuser', password='testpassword')
        self.read_group = Group.objects.create(name="Read Access 2")
        GroupProfile.objects.create(api_write_access=False, group=self.read_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.read_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.transient = TcsTransientObjects.objects.create(id=900000007, ra_psf=16.0, dec_psf=-11.0, date_inserted=now())

    def tearDown(self):
        self.transient.delete()

    def test_get_single_object(self):
        response = self.client.get('/api/objects/', {'objects': str(self.transient.id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['object']['id'], self.transient.id)

    def test_rejects_too_many_objects(self):
        objects = ','.join(str(n) for n in range(50_001))
        response = self.client.get('/api/objects/', {'objects': objects})
        self.assertIn('info', response.data)
