from django.core.management.base import BaseCommand, CommandError
from hs_core.factories import create_initial_pages
from mezzanine.pages.models import Page

class Command(BaseCommand):
    help = "Create base pages for a Hydroshare site"

    def handle(self, *args, **options):
        Page.objects.all().delete()
        create_initial_pages()
        print "Created initial pages for TOU, privacy, resource creation, and resource listing"
