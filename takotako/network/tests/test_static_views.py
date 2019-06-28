from django.test import TestCase
from django.urls import reverse


class ClientTest(TestCase):
    """
    Test suite for the django server, verifying views return expected templates
    """

    def test_s1_index(self):
        """
        Basic test
        """
        response = self.client.get(reverse('network:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello network mate")

    def test_s2_index_default_inv(self):
        """
        Basic test
        """
        response = self.client.get(reverse('network:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inventory is loaded")
        self.assertContains(response, "home-sw01")
