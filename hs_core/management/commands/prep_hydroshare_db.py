from django.core.management.base import BaseCommand, CommandError
from hs_core.factories import create_initial_pages
from django.db import connection

class Command(BaseCommand):
    help = "Create base pages for a Hydroshare site"

    def handle(self, *args, **options):
        with connection.cursor() as c:
            c.execute('create extension if not exists postgis')
            c.execute('create extension if not exists hstore')
        print "Prepared database with HStore and PostGIS extensions"
