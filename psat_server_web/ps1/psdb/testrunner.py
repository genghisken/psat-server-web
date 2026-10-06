from django.test.runner import DiscoverRunner


class NoDbCreationTestRunner(DiscoverRunner):
    """Skips test-database creation/teardown — runs tests directly against
    the database in DATABASES['default'], since the configured DB user has
    no CREATE DATABASE privilege and the schema isn't Django-managed."""

    def setup_databases(self, **kwargs):
        return []

    def teardown_databases(self, old_config, **kwargs):
        pass
