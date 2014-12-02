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
              pass
        print "Created all available test resources. To define new test resources, define them in a function called create_test_resources() in your app's factories.py"

       

