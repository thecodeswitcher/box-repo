from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

CREATE_USER_URL = reverse("user:create")
ACCOUNT_URL = reverse("user:account-list")
TOKEN_URL = reverse("user:token")
# ME_URL = reverse("user:me")

ACCOUNT_TYPE_FREE = "FREE"


def create_user(**params):
    return get_user_model().objects.create_user(**params)

class UserApiTests(TestCase):
    """Test the users API works for creating users """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test that creating a user with a valid payload is successful"""
        payload = {
            "username": "test@boxrepo.com",
            "password": "testpass",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user = get_user_model().objects.get(id=res.data["id"])
        self.assertEqual(res.data["id"], user.id)
        self.assertNotIn("password", res.data)
        self.assertIn("token", res.data)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {"username": "test@boxrepo.com", "password": "testpass"}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(username="test@boxrepo.com", password="testpass")
        payload = {"username": "test@boxrepo.com", "password": "wrong"}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class AccountApiTests(TestCase):
    """Test that API works for creating accounts"""

    def setUp(self):
        self.client = APIClient()        
        payload = {
            "username": "test@boxrepo.com",
            "password": "testpass",
        }
        logger.info(f"AccountApiTests.setUp: payload {payload}")
        res = self.client.post(CREATE_USER_URL, payload)
        self.user = get_user_model().objects.get(id=res.data["id"])
        self.client.force_authenticate(user = self.user)
    
    def test_create_valid_account_success(self):
        self.client.force_authenticate(user = self.user)
        payload = {
            "account_name": "Account 1",
            "user": self.user.id,
            "account_type": ACCOUNT_TYPE_FREE,
        }
        res = self.client.post(ACCOUNT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["user"], self.user.id)
        self.assertEqual(res.data["account_type"], ACCOUNT_TYPE_FREE)
    
    def test_only_user_can_create_account_for_self(self):
        user_payload = {
            "username": "other_user@boxrepo.com",
            "password": "testpass2",
        }
        res = self.client.post(CREATE_USER_URL, user_payload)
        other_user = get_user_model().objects.get(id=res.data["id"])
        self.client.force_authenticate(user = other_user)
        payload = {
            "account_name": "Account 2",
            "user": self.user.id,
        }
        res = self.client.post(ACCOUNT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

