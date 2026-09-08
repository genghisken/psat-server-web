from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsAPIUsageLog, TcsTransientObjects


class TestUsageLogging(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='loguser', password='testpassword')
        self.read_group = Group.objects.create(name="Read Access 3")
        GroupProfile.objects.create(api_write_access=False, group=self.read_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.read_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.transient = TcsTransientObjects.objects.create(id=900000008, ra_psf=17.0, dec_psf=-12.0, date_inserted=now())

    def tearDown(self):
        TcsAPIUsageLog.objects.filter(endpoint='/api/objects/').delete()
        self.transient.delete()

    def test_get_request_creates_usage_log_row(self):
        self.assertEqual(TcsAPIUsageLog.objects.count(), 0)
        self.client.get('/api/objects/', {'objects': str(self.transient.id)})
        self.assertEqual(TcsAPIUsageLog.objects.count(), 1)
        row = TcsAPIUsageLog.objects.first()
        self.assertEqual(row.endpoint, '/api/objects/')
        self.assertEqual(row.user, 'loguser')
        self.assertEqual(row.validated_data['objects'], str(self.transient.id))
