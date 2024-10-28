from django.apps import AppConfig


class ATLASWebConfig(AppConfig):
    name = 'atlas'

    def ready(self) -> None:
        import atlas.signals