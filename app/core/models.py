"""Database models"""

import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
        AbstractBaseUser,
        BaseUserManager,
        PermissionsMixin,)


def recipe_image_file_path(instance, filename):
    """function for creating path for file"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """manager for user"""

    def create_user(self, email, password=None, **kwargs):
        """create save and return new user"""
        if not email:
            raise ValueError('user must have email')
        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **kwargs):
        """function for creating superuser"""

        user = self.model(email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User model"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe model"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return f'{self.title}'


class Tag(models.Model):
    """tag model for filtering recipes"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    '''ingredient model'''
    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.name}'
