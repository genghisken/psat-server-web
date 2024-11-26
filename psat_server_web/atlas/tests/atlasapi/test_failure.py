import unittest

from django.test import TestCase

class TestFailure(TestCase):
    @unittest.skip("Skipping this test")
    def test_failure(self):
        assert False