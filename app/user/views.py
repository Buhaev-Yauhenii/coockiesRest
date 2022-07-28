'''Views for user model'''

from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import (UserSerializer,
        AuthTokenSerializer)

class CreateUserAPIView(generics.CreateAPIView):
    """class for create view of user"""
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """Create new token"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

