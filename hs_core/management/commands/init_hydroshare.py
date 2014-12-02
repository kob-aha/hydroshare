from hs_core.factories import create_initial_pages
from mezzanine.pages.models import Page
import importlib
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Create base pages for a Hydroshare site"

    def handle(self, *args, **options):
        from django.conf import settings
        Page.objects.all().delete()
        for app in settings.INSTALLED_APPS:
           try:
              f = importlib.import_module(app + '.factories')
              if hasattr(f, 'create_initial_data'):
                  f.create_initial_data(*args, **options)
                  print 'Creating initial data for ' + app + '.'
           except ImportError:
              print app + " has no module factories"
        print "Created all available test resources"

       

