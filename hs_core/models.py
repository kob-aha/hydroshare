from django.contrib.contenttypes import generic
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.utils.timezone import now
from mezzanine.pages.models import Page, RichText
from mezzanine.pages.page_processors import processor_for
from uuid import uuid4
from mezzanine.core.models import Ownable
from mezzanine.generic.fields import CommentsField
from mezzanine.conf import settings as s
from mezzanine.generic.models import Keyword, AssignedKeyword
import os.path
from django_irods.storage import IrodsStorage
# from dublincore.models import QualifiedDublinCoreElement
from dublincore import models as dc
from django.conf import settings
from django.core.files.storage import DefaultStorage
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from languages_iso import languages as iso_languages
from dateutil import parser
import json


