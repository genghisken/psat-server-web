from django.apps import AppConfig


class PS1AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        import accounts.signals
