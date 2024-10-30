from django.apps import AppConfig


class ATLASAccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        import accounts.signals