'''tests for views of ingredient'''

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core import models
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detailed_url(ingredient_id: int) -> str:
    '''url for detailed information of ingredient'''
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email: str = 'test@example.com',
                password: str = 'samplepassword123') -> dict[str:str]:
    '''create new user'''
    return get_user_model().objects.create_user(email, password)


class PublicIngredientTests(TestCase):
    """tests for ingredients"""
    def setUp(self) -> None:
        '''creating main env'''
        self.client = APIClient()

    def test_ingredient_list(self) -> None:
        """check ingredients list"""
        user = create_user()
        models.Ingredient.objects.create(user=user, name='ingr1')
        models.Ingredient.objects.create(user=user, name='ingr2')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientTests(TestCase):
    """test fo auth user"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_list_ingredients_for_auth_users(self) -> None:
        """check list of ingredients for auth users"""
        models.Ingredient.objects.create(user=self.user, name='ingredient 1')
        models.Ingredient.objects.create(user=self.user, name='ingredient2')

        ingredients = models.Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self) -> None:
        """Test list of ingredients is limited to authenticated user."""
        user2: dict[str:str] = create_user(email='user2@example.com')
        models.Ingredient.objects.create(user=user2, name='Salt')
        ingredient: dict[str:str] = models.Ingredient.objects.create(
                                                                user=self.user,
                                                                name='Pepper')

        res: dict[str:str] = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """tests for update information about updating inredient"""
        ing = models.Ingredient.objects.create(user=self.user, name='title')
        payload = {'name': 'New title'}
        url = detailed_url(ing.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ing.refresh_from_db()
        self.assertEqual(ing.name, payload['name'])

    def test_delete_ingredient(self):
        """test for deleting ingredients"""
        ingredient = models.Ingredient.objects.create(user=self.user,
                                                      name='ingredient')
        url = detailed_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingredients = models.Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())
