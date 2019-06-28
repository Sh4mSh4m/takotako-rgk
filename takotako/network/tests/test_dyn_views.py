from django.test import TestCase
from django.urls import reverse


class WorkflowTest(TestCase):
    """
    Test suite for the django server, verifying views return expected templates
    """

    def test_w1_index(self):
        """
        Basic test
        """
        response = self.client.get(reverse('network:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello network mate")
