__author__ = 'Pabitra'
from django.test import TestCase
from hs_core import hydroshare
from hs_core.hydroshare import resource
from hs_core.hydroshare import users
from hs_core.models import GenericResource, Bags
from django.contrib.auth.models import User
import datetime as dt


class TestCreateUser(TestCase):

    def test_create_user(self):

        # create a user
        hydroshare.create_group(name="Hydroshare Author")
        user = users.create_account(
            'dtarb@usu.edu',
            username='sometestuser',
            first_name='some_first_name',
            last_name='some_last_name',
            superuser=False,
            groups=[])

        self.assertNotEquals(None,user)