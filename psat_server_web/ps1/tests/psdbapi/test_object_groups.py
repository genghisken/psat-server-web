from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import GroupProfile
from psdb.models import TcsTransientObjects, TcsObjectGroups, TcsObjectGroupDefinitions


class TestObjectGroupsInsert(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.write_group = Group.objects.create(name="Write Access")
        GroupProfile.objects.create(api_write_access=True, group=self.write_group, token_expiration_time=timedelta(days=365))
        self.user.groups.add(self.write_group)
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.transient = TcsTransientObjects.objects.create(id=900000001, ra_psf=10.0, dec_psf=-5.0, date_inserted=now())
        self.group_def = TcsObjectGroupDefinitions.objects.create(id=60001, name='Test Group')

    def tearDown(self):
        # tcs_transient_objects/tcs_object_group_definitions/tcs_object_groups are
        # MyISAM (non-transactional) — TestCase's automatic rollback doesn't apply,
        # so rows created here must be deleted explicitly.
        TcsObjectGroups.objects.filter(transient_object_id=self.transient.id).delete()
        self.transient.delete()
        self.group_def.delete()

    def test_insert_creates_row(self):
        response = self.client.post('/api/objectgroups/', {'objectid': self.transient.id, 'objectgroupid': self.group_def.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            TcsObjectGroups.objects.filter(transient_object_id=self.transient.id, object_group_id_id=self.group_def.id).exists()
        )

    def test_insert_rejects_missing_object(self):
        response = self.client.post('/api/objectgroups/', {'objectid': 999999999, 'objectgroupid': self.group_def.id})
        self.assertEqual(response.data['info'], 'Object does not exist.')

    def test_insert_rejects_missing_group(self):
        response = self.client.post('/api/objectgroups/', {'objectid': self.transient.id, 'objectgroupid': 60002})
        self.assertEqual(response.data['info'], 'Object group ID does not exist.')
