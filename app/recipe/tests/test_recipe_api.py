"""Tests for recipe app"""

from decimal import Decimal
from typing import Any

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (Recipe, Tag, Ingredient)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer, )

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Function for creation url for one recipe"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **kwargs):
    """function to create a recipe"""
    defaults = {
        'title': 'test recipe',
        "time_minutes": 5,
        'price': Decimal('6.32'),
        'description': 'test recipe description',
        'link': 'http://example.com'
    }
    defaults.update(kwargs)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**kwargs):
    """function for creating a user"""
    return get_user_model().objects.create_user(**kwargs)


class PublicRecipeAPITest(TestCase):
    """Tests for unauth recipe API"""
    def SetUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """test is auth needed"""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """test for auth user"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client.force_authenticate(user=self.user)

    def is_ingredient_exist(self, recipe, kwargs):
        '''check is ingr exists'''
        for ingr in kwargs['ingredients']:
            is_exist = recipe.ingredients.filter(
                    name=ingr['name'],
                    user=self.user).exists()
            self.assertTrue(is_exist)

    def test_retrive_recipes(self):
        """test retrieve recipes"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')

        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_list_recipes_limited_user(self):
        """list of recipes is limitedto  auth user"""
        other_user = create_user(
            email='anotheUser@exampl.com',
            password='anotherpassword123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_detail_recipe(self):
        """check is we create detail of recipe"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """test for check creation of recipe"""
        payload = {
            'title': 'test recipe',
            "time_minutes": 5,
            'price': Decimal('6.32'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial updates"""
        original_link = 'http://example.com'
        recipe = create_recipe(
            user=self.user,
            title='test recipe',
            link=original_link,
        )
        payload = {
            'title': 'new recipe',
        }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """check full update"""
        original_link = 'http://example.com'
        recipe = create_recipe(
            user=self.user,
            title='test recipe',
            link=original_link,
            description='test description',
        )
        payload = {
            'title': 'new recipe',
            'link': 'http://example2.com',
            'description': 'new description',
            'time_minutes': 3,
            'price': Decimal('5.23')
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_tag(self) -> None:
        """check is we can to create a recipe with a tag"""
        payload: dict[str, Any] = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res: dict[str, Any] = self.client.post(
                                        RECIPES_URL,
                                        payload,
                                        format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists: bool = recipe.tags.filter(
                                            name=tag['name'],
                                            user=self.user,
                                            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self) -> None:
        """Test creating a recipe with existing tag."""
        tag_indian: dict[str, Any] = Tag.objects.create(
                                    user=self.user,
                                    name='Indian')
        payload: dict[str, Any] = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res: dict[str, Any] = self.client.post(RECIPES_URL,
                                               payload,
                                               format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes: dict[str, Any] = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe: dict[str, Any] = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists:  dict[str, Any] = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_reate_tag_with_update(self) -> None:
        """check update recipe with tag update"""
        recipe: dict[str: str] = create_recipe(user=self.user)
        payload: dict[str: str] = {
             'tags': [{'name': 'some'}], }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='some')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self) -> None:
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast: dict[str: str] = Tag.objects.create(
                                                           user=self.user,
                                                           name='Breakfast')
        recipe: dict[str: str] = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch: dict[str: str] = Tag.objects.create(
                                    user=self.user,
                                    name='Lunch')
        payload: dict[str: str] = {'tags': [{'name': 'Lunch'}]}
        url: str = detail_url(recipe.id)
        res: dict[str: str] = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self) -> None:
        """Test clearing a recipes tags."""
        tag: dict[str: str] = Tag.objects.create(user=self.user,
                                                 name='Dessert')
        recipe: dict[str: str] = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload: dict[str: str] = {'tags': []}
        url: str = detail_url(recipe.id)
        res: dict[str: str] = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_ingredients_for_recipe(self) -> None:
        """test for creating ingredients"""
        payload = {
                'title': 'new title',
                'time_minutes': 60,
                'price': Decimal('20.20'),
                'ingredients': [{'name': 'ingredient'},
                                {'name': 'another ingredient'}]}

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.is_ingredient_exist(recipe, payload)

    def test_create_recipe_with_existing_ingredients(self) -> None:
        """check create recipe with existing ingredients"""
        ingredient = Ingredient.objects.create(user=self.user, name='Solt')
        payload = {
            'title': 'new recipe',
            'time_minutes': 50,
            'price': Decimal('22'),
            'ingredients': [{'name': 'Solt'}, {'name': 'cherry'}], }
        res: dict[str:str] = self.client.post(RECIPES_URL,
                                              payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe: dict[str:str] = recipes[0]
        self.assertAlmostEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingr in payload['ingredients']:
            is_exist = recipe.ingredients.filter(
                    name=ingr['name'],
                    user=self.user).exists()
            self.assertTrue(is_exist)

    def test_create_ingredient_when_update_recipe(self) -> None:
        """test for creating a new ingredient when update recipe"""
        recipe = create_recipe(user=self.user)
        payload = {'ingredients': [{'name': 'shugar'}],
                   'price': Decimal('33'), }
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingr = Ingredient.objects.get(user=self.user, name='shugar')
        self.assertIn(new_ingr, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self) -> None:
        """Test assigning an existing ingredient when updating a recipe."""
        ingredient_breakfast: dict[str: str] = Ingredient.objects.create(
                                                           user=self.user,
                                                           name='Breakfast')
        recipe: dict[str: str] = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient_breakfast)

        ingredients_lunch: dict[str: str] = Ingredient.objects.create(
                                    user=self.user,
                                    name='Lunch')
        payload: dict[str: str] = {'ingredients': [{'name': 'Lunch'}]}
        url: str = detail_url(recipe.id)
        res: dict[str: str] = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredients_lunch, recipe.ingredients.all())
        self.assertNotIn(ingredient_breakfast, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self) -> None:
        """Test clearing a recipes ingredients."""
        ingredient: dict[str: str] = Ingredient.objects.create(user=self.user,
                                                               name='Dessert')
        recipe: dict[str: str] = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient)

        payload: dict[str: str] = {'ingredients': []}
        url: str = detail_url(recipe.id)
        res: dict[str: str] = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
