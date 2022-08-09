"""Serializers for Recipe model"""

from typing import Any
from core.models import Recipe, Tag, Ingredient

from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
    """serializer for ingredients"""

    class Meta:
        model = Ingredient
        fields: list[str] = ['id', 'name']
        read_only_fields: list[str] = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag"""

    class Meta:
        model = Tag
        fields: list[str] = ['id', 'name']
        read_only_fields: list[str] = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    tags: Any = TagSerializer(many=True, required=False)
    ingredients: Any = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields: list[str] = [
            'id',
            'title',
            'price',
            'time_minutes',
            'link',
            'tags',
            'ingredients', ]
        read_only_fields: dict[str] = ['id']

    def _get_or_create_element(self, tags, recipe) -> Any:
        """function for checking tag or creation it"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag, )
            recipe.tags.add(tag_obj)
        return recipe

    def _get_or_create_ingredient(self, ingredients, recipe) -> Any:
        """function for checking tag or creation it"""
        auth_user = self.context['request'].user
        for ingredient in ingredients:
            tag_obj, created = Ingredient.objects.get_or_create(
                user=auth_user,
                **ingredient, )
            recipe.ingredients.add(tag_obj)
        return recipe

    def create(self, validated_data) -> Any:
        """Create a Recipe with custom tags"""
        tags: list[str] = validated_data.pop('tags', [])
        ingredients: list[str] = validated_data.pop('ingredients', [])
        recipe: dict[str, str] = Recipe.objects.create(**validated_data)
        self._get_or_create_ingredient(ingredients, recipe)
        self._get_or_create_element(tags, recipe)
        return recipe

    def update(self, instance, validated_data) -> Any:
        """function for update recipe"""
        tags: dict[str: str] = validated_data.pop('tags', None)
        ingredients: list[str] = validated_data.pop('ingredients', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_element(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredient(ingredients, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe"""

    class Meta(RecipeSerializer.Meta):

        fields: dict[str] = RecipeSerializer.Meta.fields + ['description']
