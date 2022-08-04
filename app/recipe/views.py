"""
Views for recipe API
"""

from rest_framework import (
    viewsets,
    mixins, )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag, )

from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """
    view set for recipe API
    """

    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """retrieve recipe for auth user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """return the valid serializer class"""
        if self.action == 'list':
            return serializers.RecipeSerializer
        return serializers.RecipeDetailSerializer

    def perform_create(self, serializer):
        """create a new recipe"""
        serializer.save(user=self.request.user)


class TagAPIView(
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    """Views for TAG models."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """get all tags for auth user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
