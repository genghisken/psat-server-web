from django.test import TestCase

class TestFailure(TestCase):
    def test_failure(self):
        assert False