"""Serializers for Recipe model"""

from typing import Any
from core.models import Recipe, Tag

from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag"""

    class Meta:
        model = Tag
        fields: list[str] = ['id', 'name']
        read_only_fields: list[str] = ['id']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe model"""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields: list[str] = [
            'id',
            'title',
            'price',
            'time_minutes',
            'link',
            'tags', ]
        read_only_fields: dict[str] = ['id']

    def _get_or_create_tags(self, tags, recipe) -> Any: 
        """function for checking tag or creation it"""
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag, )
            recipe.tags.add(tag_obj)
        return recipe

    def create(self, validated_data) -> Any:
        """Create a Recipe with custom tags"""
        tags: list[str] = validated_data.pop('tags', [])
        recipe: dict[str, str] = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)
        return recipe 

    def update(self, instance, validated_data) -> Any:
        """function for update recipe"""
        tags: dict[str: str] = validated_data.pop('tags', None)
        if tags is not None: 
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for Recipe"""

    class Meta(RecipeSerializer.Meta):

        fields: dict[str] = RecipeSerializer.Meta.fields + ['description']
