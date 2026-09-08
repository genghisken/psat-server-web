import unittest

from django.test import TestCase

from psdbapi.serializers import ObjectListSerializer
from psdb.apiutils import buildObjectListQueryFilter


FILTER_FIELDS = [
    'rb_pix_gte', 'rb_pix_lte',
    'ra_gte', 'ra_lte',
    'dec_gte', 'dec_lte',
    'sherlock_class', 'spec_type',
]

EMPTY_VALIDATED_DATA = {
    'rb_pix_gte': None, 'rb_pix_lte': None,
    'ra_gte': None, 'ra_lte': None,
    'dec_gte': None, 'dec_lte': None,
    'sherlock_class': None, 'spec_type': None,
}


class TestObjectListSerializerFilters(TestCase):
    def test_filters_default_to_none_when_absent(self):
        serializer = ObjectListSerializer(data={'objectlistid': 0})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        for field in FILTER_FIELDS:
            self.assertIsNone(serializer.validated_data[field])

    def test_no_vra_fields_exist(self):
        serializer = ObjectListSerializer(data={'objectlistid': 0})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('vra_gte', serializer.validated_data)
        self.assertNotIn('vra_lte', serializer.validated_data)

    def test_numeric_filters_accept_valid_floats(self):
        data = {'objectlistid': 0, 'rb_pix_gte': 0.5, 'dec_lte': 5.0}
        serializer = ObjectListSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['rb_pix_gte'], 0.5)
        self.assertEqual(serializer.validated_data['dec_lte'], 5.0)

    def test_numeric_filter_rejects_non_numeric_value(self):
        serializer = ObjectListSerializer(data={'objectlistid': 0, 'rb_pix_gte': 'nope'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('rb_pix_gte', serializer.errors)


class TestBuildObjectListQueryFilter(unittest.TestCase):
    def test_empty_validated_data_returns_empty_filter(self):
        self.assertEqual(buildObjectListQueryFilter(EMPTY_VALIDATED_DATA), {})

    def test_numeric_bounds_map_to_orm_lookups(self):
        data = dict(EMPTY_VALIDATED_DATA, rb_pix_gte=0.8, dec_lte=0.9)
        self.assertEqual(
            buildObjectListQueryFilter(data),
            {'rb_pix__gte': 0.8, 'dec__lte': 0.9},
        )

    def test_string_fields_map_to_exact_match_lookups(self):
        data = dict(EMPTY_VALIDATED_DATA, sherlock_class='SN', spec_type='confirmed')
        self.assertEqual(
            buildObjectListQueryFilter(data),
            {'sherlockClassification': 'SN', 'observation_status': 'confirmed'},
        )
