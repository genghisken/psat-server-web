import unittest

from django.test import TestCase

from atlasapi.serializers import ObjectListSerializer
from atlas.apiutils import buildObjectListQueryFilter


NEW_FILTER_FIELDS = [
    'vra_gte', 'vra_lte',
    'rb_pix_gte', 'rb_pix_lte',
    'ra_gte', 'ra_lte',
    'dec_gte', 'dec_lte',
    'sherlock_class', 'spec_type',
]

EMPTY_VALIDATED_DATA = {
    'vra_gte': None, 'vra_lte': None,
    'rb_pix_gte': None, 'rb_pix_lte': None,
    'ra_gte': None, 'ra_lte': None,
    'dec_gte': None, 'dec_lte': None,
    'sherlock_class': None, 'spec_type': None,
}


class TestObjectListSerializerFilters(TestCase):
    def test_filters_default_to_none_when_absent(self):
        serializer = ObjectListSerializer(data={'objectlistid': 4})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        for field in NEW_FILTER_FIELDS:
            self.assertIsNone(serializer.validated_data[field])

    def test_numeric_filters_accept_valid_floats(self):
        data = {
            'objectlistid': 4,
            'vra_gte': 0.8, 'vra_lte': 1.0,
            'rb_pix_gte': 0.5, 'rb_pix_lte': 0.9,
            'ra_gte': 10.0, 'ra_lte': 20.0,
            'dec_gte': -5.0, 'dec_lte': 5.0,
        }
        serializer = ObjectListSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['vra_gte'], 0.8)
        self.assertEqual(serializer.validated_data['dec_lte'], 5.0)

    def test_numeric_filter_rejects_non_numeric_value(self):
        serializer = ObjectListSerializer(data={'objectlistid': 4, 'vra_gte': 'not-a-number'})
        self.assertFalse(serializer.is_valid())
        self.assertIn('vra_gte', serializer.errors)

    def test_string_filters_accept_values(self):
        data = {'objectlistid': 4, 'sherlock_class': 'SN', 'spec_type': 'confirmed'}
        serializer = ObjectListSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['sherlock_class'], 'SN')
        self.assertEqual(serializer.validated_data['spec_type'], 'confirmed')


class TestBuildObjectListQueryFilter(unittest.TestCase):
    def test_empty_validated_data_returns_empty_filter(self):
        self.assertEqual(buildObjectListQueryFilter(EMPTY_VALIDATED_DATA), {})

    def test_numeric_bounds_map_to_orm_lookups(self):
        data = dict(EMPTY_VALIDATED_DATA, vra_gte=0.8, rb_pix_lte=0.9)
        self.assertEqual(
            buildObjectListQueryFilter(data),
            {'vra__gte': 0.8, 'rb_pix__lte': 0.9},
        )

    def test_string_fields_map_to_exact_match_lookups(self):
        data = dict(EMPTY_VALIDATED_DATA, sherlock_class='SN', spec_type='confirmed')
        self.assertEqual(
            buildObjectListQueryFilter(data),
            {'sherlockClassification': 'SN', 'observation_status': 'confirmed'},
        )

    def test_unrelated_keys_are_ignored(self):
        data = {'objectlistid': 4, 'getcustomlist': False, 'datethreshold': None}
        self.assertEqual(buildObjectListQueryFilter(data), {})
