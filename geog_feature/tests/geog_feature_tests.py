__author__ = 'jeff'

import unittest
from hs_core.hydroshare import get_resource_by_shortkey
from hs_core.hydroshare.resource import add_resource_files, create_resource, get_resource_map
from django.contrib.auth.models import User, Group
from hs_core import hydroshare

class test_geog_resource_creation(unittest.TestCase):

    def setUp(self):

        pass

    def tearDown(self):
        User.objects.filter(username='shaun').delete() #delete user after test is done

    def test_add_files(self):
        group, _ = Group.objects.get_or_create(name='Hydroshare Author')
        user = list(User.objects.all())   #create user
        l = []
        user1 = hydroshare.create_account(
                'user1@nowhere.com',
                username='user1',
                first_name='Creator_FirstName',
                last_name='Creator_LastName',
                superuser=False,
                groups=[group]
            )
        #
        res1 = create_resource('GenericResource', user1, 'res1')   #create resource

        self.assertEqual(res1.title, 'res1')
        self.assertEqual(user1.username, 'user1')
        self.assertEqual(type(user), type(l))
        self.assertEqual(len(user), 0)
        self.assertTrue(1 == 1, 'something is happeing')