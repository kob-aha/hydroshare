from django.db import models
from mezzanine.pages.models import Page
from hs_core.models import AbstractResource
from hs_core.models import resource_processor
from mezzanine.pages.page_processors import processor_For

# Create your models here.


class GeogFeature(Page, AbstractResource):
    pass