"""Tests for tags API."""
from decimal import Decimal
from typing import Any
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (Tag, Recipe)
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def create_user(email='user@example.com', password='password123'):
    """function for creating a user"""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(tag_id: int) -> str:
    """Create and return a tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])


class PublicTagAPITest(TestCase):
    """Tests for tag api for unauthenticated users"""
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        """Test auth required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTAGsTest(TestCase):
    """tests for private tags"""
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_etrieve_tags(self):
        """test retrieving list of tags"""
        Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=self.user, name='spicy')

        res: str = self.client.get(TAGS_URL)
        tags: dict[str: str] = Tag.objects.all().order_by('-name')

        serializer: Any = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_recipes_limited_user(self) -> None:
        """list of tags is limited to  auth user"""
        other_user = create_user(
            email='anotheUser@exampl.com',
            password='anotherpassword123',
        )
        tag: dict[str:str] = Tag.objects.create(user=self.user, name='vegan')
        Tag.objects.create(user=other_user, name='vegan')

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_updating_tag(self) -> None:
        """test for update tags"""
        tag: dict[str:str] = Tag.objects.create(
            user=self.user,
            name='original name', )
        payload: dict[str:str] = {
            'name': 'changed name',
        }
        url: str = detail_url(tag.id)
        res: dict[str:str] = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.id, tag.id)
        self.assertEqual(tag.user, self.user)

    def test_delete_tag(self) -> None:
        """test for deleting tag"""
        tag: dict[str, str] = Tag.objects.create(
                                        user=self.user, name='new tag')

        url: str = detail_url(tag.id)
        res: dict[str:str] = self.client.delete(url,)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags: dict[str, str] = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_asigning_recipe(self):
        """test for filtering recipe by ingredients"""
        tag1 = Tag.objects.create(user=self.user, name="tag1")
        tag2 = Tag.objects.create(user=self.user, name="tag2")
        recipe = Recipe.objects.create(
            title='recipe',
            time_minutes=22,
            price=Decimal('44.2'),
            user=self.user,
        )
        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assignet_only': 1})

        t1 = TagSerializer(tag1)
        t2 = TagSerializer(tag2)
        self.assertIn(t1.data, res.data)
        self.assertNotIn(t2.data, res.data)

    def test_filter_ingredients_unique(self):
        """test is ingredients returned list is unique"""
        tag1 = Tag.objects.create(user=self.user, name="tag1")
        Tag.objects.create(user=self.user, name="tag2")
        recipe = Recipe.objects.create(
            user=self.user,
            title="recipe",
            time_minutes=32,
            price=Decimal('12.2')
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title="recipe2",
            time_minutes=12,
            price=Decimal('52.2')
        )
        recipe.tags.add(tag1)
        recipe2.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assignet_only': 1})
        self.assertEqual(len(res.data), 1)
