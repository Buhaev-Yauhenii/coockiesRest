"""tests for models"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from decimal import Decimal

from core import models


def create_user(email='email@example.com', password='password123'):
    """Create a user for tests"""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    """test for models"""

    def test_create_user_with_email_successful(self):
        """check create email in usermodel"""
        email = "test@example.com"
        password = 'testpass123'
        user = get_user_model().objects.create_user(email=email,
                                                    password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """test email normalize for new users"""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'], ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email=email,
                                                        password='sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """test that creating user without an email raises a ValueError"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample123')

    def test_create_superuser(self):
        """test for creating superuser"""

        user = get_user_model().objects.create_superuser(
                'test@test.com',
                'test123',)

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """test for creating recipe"""
        user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='test recipe',
            time_minutes=5,
            price=Decimal('6.32'),
            description='test recipe description', )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """test for creating tag"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='test_tag')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """test for create a new ingredient"""
        user = create_user()
        ingredient = models.Ingredient.objects.create(user=user, name='ingredient')

        self.assertEqual(str(ingredient), ingredient.name)
