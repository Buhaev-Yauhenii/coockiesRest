"""
Tests for user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

def create_user(**kwargs):
    """Create and return new user"""
    return get_user_model().objects.create_user(**kwargs)

class PublicUserAPITests(TestCase):
    """test public API methods"""
    def SetUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """test creating new user"""
        user_args = {
                "email":'test@test.test',
                'password':'example123',
                'name':'test_name',}
        res = self.client.post(CREATE_USER_URL, user_args)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=user_args['email'])
        self.assertTrue(user.check_password(user_args['password']))
        self.assertNotIn('password', res.data)
    def test_user_password_exists_errors(self):
        """test is password exists and errors about this"""
        user_args = {
                'email': 'test@test.test',
                'password': 'example123',
                'name': 'test_name'}
        create_user(**user_args)
        res = self.client.post(CREATE_USER_URL, user_args)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    def test_short_password_error(self):
        """test is password to short"""
        user_args = {
                'email': 'test@test.test',
                'password': 'ex',
                'name': 'test_name'
                }
        res = self.client.post(CREATE_USER_URL, user_args)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=user_args['email']).exists()
        self.assertFalse(user_exists)
        
    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        create_user(**user_details)

        payload = {
            'email': 'test@example.com',
            'password': 'test-user-password123',
        }
        res = self.client.post(TOKEN_URL, payload)
        print(res.data)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='goodpass')

        payload = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_email_not_found(self):
        """Test error returned if user not found for given email."""
        payload = {'email': 'test@example.com', 'password': 'pass123'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)