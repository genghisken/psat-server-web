import os
import sys

sys.path.append('GENERIC_FILESYSTEM/code/web/atlas')
os.environ['DJANGO_SETTINGS_MODULE'] = 'atlas.settings'
os.environ['PYTHON_EGG_CACHE'] = '/files/django_websites/egg_cache'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
