"""tests for admin panel"""

from django.test import (TestCase, Client)
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):
    """test for django admin"""

    def setUp(self):
        """create user and client"""

        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
                email='admin@test.com',
                password='pass123', )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
                email='user@example.com',
                password='testpass123',
                name='test_user', )

    def test_users_list(self):
        """test that users are in list on the page"""

        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        """test of edit page"""

        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """test of creating user page"""

        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
