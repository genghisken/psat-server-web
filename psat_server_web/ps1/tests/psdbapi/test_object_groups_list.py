from django.test import TestCase
from django.utils.timezone import now
from psdbapi.serializers import TcsObjectGroupsListSerializer
from psdb.models import TcsTransientObjects, TcsObjectGroups, TcsObjectGroupDefinitions


class TestTcsObjectGroupsListSerializerValidation(TestCase):
    def test_requires_objectid_or_objectgroupid(self):
        serializer = TcsObjectGroupsListSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_no_vra_fields_exist(self):
        serializer = TcsObjectGroupsListSerializer(data={'objectgroupid': 1})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('vra_gte', serializer.validated_data)


class TestObjectGroupsListQuery(TestCase):
    def setUp(self):
        self.transient = TcsTransientObjects.objects.create(id=900000003, ra_psf=12.0, dec_psf=-7.0, date_inserted=now())
        self.group_def = TcsObjectGroupDefinitions.objects.create(id=60005, name='Test Group 3')
        TcsObjectGroups.objects.create(transient_object_id_id=self.transient.id, object_group_id_id=self.group_def.id)

    def tearDown(self):
        TcsObjectGroups.objects.filter(transient_object_id=self.transient.id).delete()
        self.transient.delete()
        self.group_def.delete()

    def test_lookup_by_objectgroupid_returns_row(self):
        serializer = TcsObjectGroupsListSerializer(data={'objectgroupid': self.group_def.id})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['transient_object_id'], self.transient.id)
