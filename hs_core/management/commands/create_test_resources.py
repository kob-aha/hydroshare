from hs_core.factories import create_initial_pages
from mezzanine.pages.models import Page
import importlib
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Create base pages for a Hydroshare site"

    def handle(self, *args, **options):
        from django.conf import settings
        for app in settings.INSTALLED_APPS:
           try:
              f = importlib.import_module(app + '.factories')
              if hasattr(f, 'create_test_resources'):
                  f.create_test_resources(*args, **options)
                  print 'Creating test resources for ' + app + '.'
           except ImportError:
              print app + " has no module factories"
        print "Created all available test resources"

       

