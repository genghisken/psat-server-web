from django.test import TestCase

from atlasapi.serializers import ObjectListSerializer


NEW_FILTER_FIELDS = [
    'vra_gte', 'vra_lte',
    'rb_pix_gte', 'rb_pix_lte',
    'ra_gte', 'ra_lte',
    'dec_gte', 'dec_lte',
    'sherlock_class', 'spec_type',
]


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
