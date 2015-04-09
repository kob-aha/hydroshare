__author__ = 'hydro'
import django.test

class TestDummy(django.test.TestCase):
    def test_dummy(self):
        self.assertEquals(1,1)

    def test_idiot(self):
        self.assertEquals(1,2)

    def test_dave(self):
        t=3/0
        self.assertEquals(1,1)


